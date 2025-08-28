import sys
from uuid import uuid4
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class ConversationalRAG:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
    
    def _load_llm(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error initializing SingleDocumentChatIngestion", error=str(e))
            raise DocumentPortalException(e, sys)
    
    def _get_session_history(self, session_id:str):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error getting session history", error=str(e))
            raise DocumentPortalException(e, sys)
        
    def load_retriver_from_fiass(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error getting retriever from FIASS", error=str(e))
            raise DocumentPortalException(e, sys)

    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error invoking SingleDocumentChatIngestion", error=str(e))
            raise DocumentPortalException(e, sys)