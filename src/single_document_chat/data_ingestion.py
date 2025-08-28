import sys
from uuid import uuid4
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader


class SingleDocumentChatIngestion:
    
    def __init__(self):
        try:
            self.log = CustomLogger().get_logger(__name__)
        except Exception as e:
            self.log.error(f"Error initializing SingleDocumentChatIngestion: {e}")
            raise DocumentPortalException(e, sys)
    
    def ingest_files(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error ingesting files: {e}")
            raise DocumentPortalException(e, sys)
    
    def _create_retriever(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException(e, sys)
    