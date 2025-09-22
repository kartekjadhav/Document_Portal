import sys

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class ConversationalRAG:
    """
    Class for Conversational RAG for multi document chat.
    """

    SUPPORTED_FILE_EXTENSIONS = [".pdf", ".docx", ".doc", ".md"]
    def __init__(self, data_dir:str="data/single_document_chat", faiss_dir:str="faiss_index", session_id:str | None =None):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            pass

        except Exception as e:
            self.logger.error("An error has occured while initialising ConversationalRAG.")
            raise DocumentPortalException(e, sys)

    def load_retriever_from_faiss(self):
        pass

    def invoke(self):
        pass

    def _load_llm(self):
        pass

    @staticmethod
    def _format_docs(docs):
        pass

    def _build_lcel_chain(self):
        pass