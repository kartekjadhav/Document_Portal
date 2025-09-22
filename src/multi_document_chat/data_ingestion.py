import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class DocumentIngestor:
    SUPPORTED_FILE_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]
    def __init__(self, data_dir:str="data/single_document_chat", faiss_dir:str="faiss_index", session_id:str | None =None):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.logger.info("Starting to initialise DocumentIngestor.")

            # Base dirs
            self.data_dir_path = Path(data_dir)
            self.faiss_dir_apth = Path(faiss_dir)
            self.data_dir_path.mkdir(parents=True, exist_ok=True)
            self.faiss_dir_apth.mkdir(parents=True, exist_ok=True)

            # session paths
            session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:8]}"
            self.session_data_path = self.data_dir_path / session_id
            self.session_faiss_path = self.faiss_dir_apth / session_id
            self.session_data_path.mkdir(parents=True, exist_ok=True)
            self.faiss_dir_path.mkdir(parents=True, exist_ok=True)

            # Model loader
            self.loader = ModelLoader()

            self.logger.info("DocumentIngestor has been initialized.")
        
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentIngestor.", error_message=e)
            raise DocumentPortalException(e, sys)

    def ingest(self, uploaded_files):
        try:
            documents = []

            for file in uploaded_files:
                ext = file.name.suffix

                if ext not in self.SUPPORTED_FILE_EXTENSIONS:
                    self.logger.warning(f"Unsupported file extension: {ext}", file=file.name)
                    continue
                
                unique_name = f"file_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}_{os.path.basename(file.name)}"
                temp_path = self.session_data_path / unique_name

                with open(temp_path, "wb") as f:
                    f.wite(file.read())

                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".txt":
                    loader = TextLoader(str(temp_path))
                elif ext == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                else:
                    self.logger.warning(f"Unsupported file extension: {ext}", file=temp_path)
                    continue

                docs = loader.load()
                documents.extend(docs)

            if not documents:
                raise DocumentPortalException(f"No valid documents found in the uploaded files.", sys)
            
            self.logger.info("Documents have been ingested successfully. Now creating retriever.", document_count=len(documents))
            return self._create_retriever(documents)

        except Exception as e:
            self.logger.error("An error has occured while ingesting documents.")
            raise DocumentPortalException(e, sys)
    
    def _create_retriever(self, documents):
        try:
            # Creating chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(documents=documents)

            # Creating embeddings.
            embedding = self.loader.load_embedding()

            # Creating FAISS vectore store
            vector_store = FAISS.from_documents(documents=chunks, embedding=embedding)
            vector_store.save_local(str(self.session_faiss_path))
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

            self.logger.info("Retriever has been created successfully.")
            return retriever

        except Exception as e:
            self.logger.error("An error has occured while creating retriever.")
            raise DocumentPortalException(e, sys)
        









        