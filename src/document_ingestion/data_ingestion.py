import os
import sys
import shutil
import json
import hashlib
import fitz
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Iterable
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from utils.file_io import generate_session_id, save_uploaded_files
from utils.document_ops import load_documents


class FaissManager:
    def __init__(self, index_dir:Path, model_loader:Optional[ModelLoader]=None):
        self.logger = CustomLogger().get_logger(__name__)
        self.logger.info("Starting to initialise FaissManager.")

        # Creating index_dir directory if not exists
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta : Dict[str, Any] = {'rows': {}}

        try:
            self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {'rows': {}}
        except Exception:
            self._meta = {'rows': {}}
        
        self.loader = model_loader or ModelLoader()
        self.emb = self.loader.load_embedding()
        self.vs : Optional[FAISS] = None

        self.logger.info("FaissManager has been initialized.")
    
    def _exists(self):
        return (self.index_dir / 'index.faiss').exists() and (self.index_dir / 'index.pickle').exists()
    
    def _fingerprint(self, text:str, md:Dict[str,Any]) -> str:
        src = md.get('source') or md.get('file_path')
        rid = md.get('row_id')
        # if md exits
        if src is not None:
            return f"{src}::{'' if rid is None else rid}"
        # if md is not given
        return hashlib.sha256(text.encode(encoding='utf-8')).hexdigest()
    
    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=True, indent=2), encoding='utf-8')

    def add_documents(self, docs:List[Document]):
        try:
            self.logger.info('Starting to add document in faiss index.')

            if not self.vs:
                raise RuntimeError("No index exists. First create index by calling load_or_create().")
            
            new_docs : List[Document] = []

            for d in docs:
                key = self._fingerprint(text=d.page_content, md=d.metadata or {})
                if key in self._meta['rows']:
                    continue
                self._meta['rows'][key] = True
                new_docs.append(d)
            
            if new_docs:
                self.vs.add_documents(documents=new_docs)
                self.vs.save_local(str(self.index_dir))
                self._save_meta()
            
            self.logger.info('Finished adding document in faiss index.')
            return len(new_docs)

        except Exception as e:
            self.logger.error("An error has occured while adding documents.")
            raise DocumentPortalException(f"An error has occured while adding documents. {str(e)}", e) from e

    def load_or_create(self, texts:Optional[List[str]]=None, metadatas:Optional[List[dict]]=None):
        try:
            self.logger.info("Loading or creating faiss.")
            
            if self._exists():
                self.vs = FAISS.load_local(
                    self.index_dir,
                    embeddings=self.emb,
                    allow_dangerous_deserialization=True
                )
                self.logger.info("Finished loading faiss.")
                return self.vs 
            
            if not texts:
                raise DocumentPortalException(f'No index exists and no data available to create index.')

            self.vs = FAISS.from_texts(texts=texts, embedding=self.emb, metadatas=metadatas or [])
            # Update metadata tracking for new documents
            for i, text in enumerate(texts):
                md = metadatas[i] if metadatas and i < len(metadatas) else {}
                key = self._fingerprint(text=text, md=md)
                self._meta['rows'][key] = True
            
            self._save_meta()
            self.vs.save_local(folder_path=str(self.index_dir))
            self.logger.info("Finished creating faiss.")
            return self.vs

        except Exception as e:
            self.logger.error("An error has occured while loading or creating faiss.")
            raise DocumentPortalException(f"An error has occured while loading or creating faiss. {str(e)}", e) from e


class DocHandler:
    def __init__(self, docs_dir:Optional[str]=None, session_id:Optional[str]=None):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            # Create docs dir if it does not exits
            self.docs_dir = docs_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), 'data', 'document_analyzer'))

            # session folder name
            self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}"
            self.session_folder_path = os.path.join(self.docs_dir, self.session_id)

            # Create session folder
            os.makedirs(self.session_folder_path)

            self.logger.info("DocHandler has been initialized.", session_id=self.session_id)

        except Exception as e:
            self.logger.error("An error has occured while initialising DocHandler.")
            raise DocumentPortalException(f"An error has occured while initialising DocHandler. {str(e)}", e) from e
        
    def save_pdf(self, uploaded_file):
        try:
            filename = uploaded_file.name
            if not filename.endswith(".pdf"):
                self.logger.error("Only pdf files are allowed.", filename=filename)
                raise DocumentPortalException(f"Only pdf files are allowed. {filename}", sys)
            
            save_path = os.path.join(self.session_folder_path, filename)
            with open(save_path, "wb") as f:
                if hasattr(uploaded_file, "read"):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.get_buffer())
            
            self.logger.info("Pdf has been saved successfully.", filename=filename, save_path=save_path)
            
            return save_path


        except Exception as e:
            self.logger.error("An error has occured while saving pdf.")
            raise DocumentPortalException(f"An error has occured while saving pdf. {str(e)}", e) from e
    

    def read_pdf(self, save_path:str):
        try:
            text_chunks= []
            with fitz.open(save_path) as docs:
                for page, doc in enumerate(docs):
                    text = doc.get_text()
                    text_chunks.append(f"\n\nPage {page+1}: {text}\n\n")
            
            self.logger.info("Pdf has been read successfully.", save_path=save_path)
            return "".join(text_chunks)

        except Exception as e:
            self.logger.error("An error has occured while reading pdf.")
            raise DocumentPortalException(f"An error has occured while reading pdf. {str(e)}", e) from e
        


class DocumentComparator:
    def __init__(self, docs_dir:str="data\document_comparer", session_id:Optional[str]=None):
        try:
            self.logger = CustomLogger().get_logger(__name__)
            self.logger.info("Starting to initialise DocumentComparator.")
            self.docs_dir = Path(docs_dir)
            self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}"
            self.session_path = self.docs_dir / self.session_id
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.logger.info("Finished initialising DocumentComparator.")
        
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentComparator.")
            raise DocumentPortalException("Error occured while initialising DocumentComparator.", e) from e
    
    def save_pdf(self, reference_file, actual_file):
        try:
            self.logger.info("Starting to save reference_file and actual_file", reference_file=reference_file.name, actual_file=actual_file.name)

            reference_file_path:Path = self.session_path / reference_file.name
            actual_file_path:Path = self.session_path / actual_file.name

            if reference_file_path.suffix != ".pdf" or actual_file_path.suffix != ".pdf":
                self.logger.error("Please upload PDF files only.", reference_file=reference_file.name, actual_file=actual_file.name)
                raise DocumentPortalException(e, sys)
            
            with open(reference_file_path, "wb") as f:
                f.write(reference_file.get_buffer())

            with open(actual_file_path, "wb") as f:
                f.write(actual_file.get_buffer())

            self.logger.info("Successfully saved reference file and actual file.")

            return reference_file_path, actual_file

        except Exception as e:
            self.logger.error("An error has occured while saving pdf.")
            raise DocumentPortalException("Error occured while saving pdf.", e) from e
        
    def read_pdf(self, pdf_path:Path):
        try:
            self.logger.info("Starting to read the pdf.", path=pdf_path)            
            
            if not pdf_path.exists():
                self.logger.error(f"Correct path not passed to read, {pdf_path} does not exists.")

            text_chunks = []
            with fitz.open(pdf_path) as docs:
                for page, doc in enumerate(docs):
                    text = doc.get_text()
                    text_chunks.append(f"\n\n Page {page} \n {text} \n\n")
            
            self.logger.info("Successfully read PDF.", path=pdf_path)
            return "".join(text_chunks)
            

        except Exception as e:
            self.logger.error("An error has occured while reading pdf.")
            raise DocumentPortalException("Error occured while reading pdf.", e) from e
    
    def combine_documents(self):
        try:
            combined_docs = []
            for file in self.session_path.iterdir():
                if file.is_file() and file.suffix == ".pdf":
                    content = self.read_pdf(file)
                    combined_docs.append(f"\n\n ------------- Document: {file.name} ------------- \n {content}")

            self.logger.info("Successfully combined all the documents.")
            return "\n\n".join(combined_docs)

        except Exception as e:
            self.logger.error("An error has occured while combining docs.")
            raise DocumentPortalException("Error occured while combining docs.", e) from e
        
    def clean_old_sessions(self, keep_latest:int=3):
        try:
            self.logger.info(f"Starting to delete old session.", keep_latest=keep_latest)
            
            sessions = sorted([session for session in self.docs_dir.iterdir() if session.is_dir()], reverse=True)

            for session in sessions[keep_latest:]:
                shutil.rmtree(session)
                self.logger.info(f"Successfully deleted {session.name}")

            self.logger.info("Successfully cleaned old sessions.", keep_latest=keep_latest)

        except Exception as e:
            self.logger.error("An error has occured while cleaning old sessions.")
            raise DocumentPortalException("Error occured while cleaning old sessions.", e) from e
        
    
class ChatIngestor:
    def __init__(
            self,
            temp_base:str='data',
            faiss_base:str='faiss_index',
            use_session_dirs:bool=True,     
            session_id:Optional[str]=None,
        ):
        try:
            self.logger = CustomLogger().get_logger(__name__)
            self.logger.info("Starting to initialise ChatIngestor.")
            
            self.temp_base = Path(temp_base)
            self.temp_base.mkdir(parents=True, exist_ok=True)
            self.temp_dir = self._resolve_dir(base=self.temp_base)

            self.faiss_base = Path(faiss_base)
            self.faiss_base.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = self._resolve_dir(base=self.faiss_base)

            self.use_session = use_session_dirs
            
            self.session_id = session_id or generate_session_id()

            self.loder = ModelLoader()
            
            self.logger.info(
                "Finished initialising ChatIngestor.",
                temp_base=self.temp_base,
                faiss_base=self.faiss_base,
                sessionized=self.use_session,
                session_id=self.session_id
            )
        except Exception as e:
            self.logger.error("An error has occured while initialising ChatIngestor.")
            raise DocumentPortalException('Initialisation of ChatIngestor Failed', e) from e
    
    def _resolve_dir(self, base:Path):
        if self.use_session:
            d = base / self.session_id # e.g - "faiss_index/abc123"
            d.mkdir(parents=True, exist_ok=True) # Created dir if not exists
            return d
        return base # Fallback to "faiss_index"
    
    def _split(self, docs: List[Document], chunk_size:int=1000, chunk_overlap:int=200) -> List[Document]:
        self.logger.info("Starting to create chunks.")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents=docs)
        self.logger.info("Finished creating chunks.")
        return chunks
    
    def build_retriever(
        self,
        uploaded_files:Iterable,
        chunk_size:int=1000,
        chunk_overlap:int=200,
        k:int=5
    ):
        try:
            self.logger.info("Starting to build retriever.")
            
            saved_paths = save_uploaded_files(uploaded_files=uploaded_files, target_dir=self.temp_dir)
            docs = load_documents(paths=saved_paths)
            chunks = self._split(docs=docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            # Create FaissManger
            fm = FaissManager(self.faiss_dir, model_loader=self.loder)

            texts = [chunk.page_content for chunk in chunks]
            metas = [chunk.metadata for chunk in chunks]

            
            vs = fm.load_or_create(texts=texts, metadatas=metas)

            added = fm.add_documents(docs=chunks)
            self.logger.info('FAISS index updated', added=added, index=str(self.faiss_dir))

            return vs.as_retriever(
                search_type="similarity",
                search_kwargs={'k': k}
            )
        except Exception as e:
            self.logger.error("An error has occured while building retriever.")
            raise DocumentPortalException("Error occured while building retriever.", e) from e