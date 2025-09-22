import os
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class SingleDocumentChatIngestion:
    def __init__(self, data_dir:str="data/single_document_chat", faiss_dir:str="faiss_index"):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.logger.info("Starting to initialise SingleDocumentChatIngestion.")
            # Create data_dir dir if not exits. 
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Create faiss db dir
            self.fiass_dir = Path(faiss_dir)
            self.fiass_dir.mkdir(parents=True, exist_ok=True)

            self.loader = ModelLoader()

            self.logger.info("SingleDocumentChatIngestion has been initialized.")

        except Exception as e:
            self.logger.error("An error has occured while initialising SingleDocumentChatIngestion.", error_message=e)
            raise DocumentPortalException(e, sys)

    def ingest_files(self, uploaded_files):
        try:
            self.logger.info("Starting to ingest files.")
            
            documents = []
            for file in uploaded_files:
                unique_name = f"file_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}_{os.path.basename(file.name)}"
                temp_path = Path(self.data_dir) / unique_name

                with open(temp_path, "wb") as f:
                    f.write(file.read())

                self.logger.info("File has been saved successfully.", path=temp_path)

                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                
                documents.extend(docs)
            
            self.logger.info("Files have been ingested successfully.", file_count=len(uploaded_files))
            return self._create_retriever(documents)

        except Exception as e:
            self.logger.error("An error has occured while ingesting files.")
            raise DocumentPortalException(e, sys)

    def _create_retriever(self, documents):
        try:
            # Creating chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(documents=documents)
            self.logger.info("Chunks have been created successfully.", chunk_count=len(chunks))

            # Loading embedding model
            embedding = self.loader.load_embedding()
            self.logger.info("Embedding model has been loaded successfully.")

            # Creating vector store and retriever.
            vector_store = FAISS.from_documents(documents=chunks, embedding=embedding)
            self.logger.info("Vector store has been created successfully.")

            # Save FAISS index, docstore, and index_to_docstore_id to disk.
            vector_store.save_local(str(self.fiass_dir))
            self.logger.info("FAISS vector store has been saved successfully.")

            # Creating retriever
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})
            self.logger.info("Retriever has been created successfully.")

            return retriever

            
        except Exception as e:
            self.logger.error("An error has occured while creating retriever.")
            raise DocumentPortalException(e, sys)