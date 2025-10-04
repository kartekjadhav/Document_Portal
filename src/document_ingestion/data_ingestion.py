from __future__ import annotations
import os
import sys
import json
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict, Any

import fitz
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

class FaissManager:
    def __init__(self, index_dir:Path, model_loader: Optional[ModelLoader]) -> None:
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta: Dict[str, Any] = {"rows": {}}

        if self.meta_path.exists():
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}}
            except:
                self._meta = {"rows": {}}

        self.model_loader = model_loader or ModelLoader()
        self.emb = self.model_loader.load_embedding()
        self.vs: Optional[FAISS] = None
    def _exists(self) -> bool:
        return (self.index_dir / "index.faiss").exists() and (self.index_dir / "index.pkl").exists() 

    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")


    @staticmethod
    def _fingerprint(text:str, md: Dict[str, Any]) -> str:
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")
        if src is not None:
            return f"{src}::{"" if rid is None else rid}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def add_documents(self, docs: List[Document]):
        if self.vs is None:
            raise RuntimeError("Call load_or_create() first before adding documents.")

        new_docs: List[Document] = []

        for d in docs:
            key = self._fingerprint(d.page_content, d.metadata or {})
            if key in self._meta["rows"]:
                continue
            self._meta[key] = True
            new_docs.append(d)
        
        if new_docs:
            self.vs.add_documents(new_docs)
            self.vs.save_local(str(self.index_dir))
            self._save_meta()

        return new_docs

    def load_or_create(self):
        if self._exists():
            self.vs = FAISS.load_local(
                folder_path=str(self.index_dir), 
                embeddings=self.emb,
                allow_dangerous_deserialization=True
            )
            return self.vs



class DocHandler:
    """
    PDF save + read (page wise) for analysis
    """
    def __init__(self, data_dir:Optional[str]=None, session_id:Optional[str]=None):
        self.logger = CustomLogger().get_logger(__name__)
        self.logger.info("Starting to initialise ChatIngestor.")

        self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analyzer")) 
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid.uuid4().hex[:6]}" 
        self.session_path = os.path.join(self.data_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)
        self.logger.info("ChatIngestor has been initialized.", session_id=self.session_id)  

    def save_pdf(self, uploaded_file) -> str:
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.endswith(".pdf"):
                self.logger.error(f"Uploaded file {filename} is not of PDF type. Please upload PDF file.", session_id = self.session_id)
                raise DocumentPortalException("Uploaded file {filename} is not of PDF type. Please upload PDF file.", sys)
        
            save_path = os.path.join(self.session_path, filename)

            with open(save_path, "wb") as f:
                if hasattr(uploaded_file, "read"):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.get_buffer())

            self.logger.info(f"File {filename} has been save successfully.", path=save_path)

            return save_path

        except Exception as e:
            raise DocumentPortalException(f"Failed to save the pdf file.{str(e)} ",e) from e

    def read_pdf(self, pdf_path:str) -> str:
        try:
            text_chunks = []
            with fitz.open(pdf_path) as docs:
                for page_num, page in enumerate(docs):
                    text = page.get_text()
                    text_chunks.append(f"\n\n-------Page no. {page_num}-------\n\n{text}")
                text = "\n".join(text_chunks)
                self.logger.info("PDF file has been read successfully.", path=pdf_path)
                return text
        except Exception as e:
            raise DocumentPortalException(f"Failed to read the pdf file.{str(e)} ",e) from e
        
    


class DocumentComparator:
    def __init__(self, base_dir:str="data/document_comparer", session_id=None):
        self.logger = CustomLogger().get_logger(__name__)
        self.logger.info("Starting to initialise DocumentComparator.")
        self.base_dir = Path(base_dir)
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.logger.info("DocumentComparator has been initialized for Document Comparer", session_id=self.session_id)


    def save_uploaded_files(self, reference_file, actual_file):
        try:
            reference_file_path = self.session_path / reference_file.name
            actual_file_path = self.session_path / actual_file.name

            if reference_file_path.suffix != ".pdf" or actual_file_path.suffix != ".pdf":
                self.logger.error("Uploaded file is not of PDF type. Please upload PDF file.", reference_file=reference_file.name, actual_file=actual_file.name)
                raise DocumentPortalException("Uploaded file is not of PDF type. Please upload PDF file.", sys)

            with open(reference_file_path, "wb") as f:
                f.write(reference_file.get_buffer())

            with open(actual_file_path, "wb") as f:
                f.write(actual_file.get_buffer())

            self.logger.info("PDF files have been saved successfully.", reference_file=reference_file.name, actual_file=actual_file.name)

            return reference_file_path, actual_file_path

        except Exception as e:
            self.logger.error("An error has occured while saving the pdf files.", reference_file=reference_file, actual_file=actual_file)
            raise DocumentPortalException("An error has occured while saving the pdf files.", e) from e

    def read_pdf(self, pdf_path:Path):
        try:
            if not pdf_path.exists():
                self.logger.error("PDF file does not exist.", pdf_path=pdf_path)
                raise DocumentPortalException("PDF file does not exist.", e) from e
            chunks = []

            with fitz.open(pdf_path) as docs:
                for page_num, page in enumerate(docs):
                    text = page.get_text()
                    chunks.append(f"\n\n-------Page no. {page_num}-------\n\n{text}")
                text = "\n".join(chunks)
                self.logger.info("PDF file has been read successfully.", pdf_path=pdf_path)
                return text
        except Exception as e:
            self.logger.error("An error has occured while reading the pdf file.", pdf_path=pdf_path)
            raise DocumentPortalException("An error has occured while reading the pdf file.", e) from e

    def combine_documents(self):
        try:
            doc_parts = []

            for file in (self.session_path.iterdir()):
                if file.is_file() and file.suffix == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"\n\n-------Document: {file.name}-------\n\n{content}")
            
            combined_docs = "\n\n".join(doc_parts)
            self.logger.info("Documents have been combined successfully.")
            return combined_docs

        except Exception as e:
            self.logger.error("An error has occured while combining the pdf files.")
            raise DocumentPortalException("An error has occured while combining the pdf files.", e) from e


    def clean_old_session(self, keep_latest:int=3):
        try:
            sessions = sorted([dir for dir in self.base_dir.iterdir() if dir.is_dir()], reverse=True)
            for dir in sessions:
                shutil.rmtree(dir)
                self.logger.info("Old session has been cleaned.", session_id=dir.name)

            self.logger.info("Old sessions have been cleaned successfully.", keep_latest=keep_latest)

        except Exception as e:
            self.logger.error("An error has occured while cleaning the old sessions.", keep_latest=keep_latest)
            raise DocumentPortalException("An error has occured while cleaning the old sessions.", e) from e


class DocumentComparatorLLM:
    def __init__(self):
        pass
    def compare_documents(self):
        pass    
    

class ChatIngestor:
    def __init__(self):
        pass

    def _resolve_dir(self):
        pass
    def _split(self):
        pass
    def build_retriever(self):
        pass

