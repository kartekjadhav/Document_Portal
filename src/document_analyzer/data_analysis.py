import os
import sys
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from utils.model_loader import ModelLoader
from models.models import *
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyzer:
    
    """
    A class to analyze documents using language models.
    Automatically logs operations and handles exceptions based on the session.
    """

    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            # prepare parsers
            self.parser = JsonOutputParser(pydantic_object=MetaData)
            self.fixing_parser = OutputFixingParser.from_llm(llm=self.llm, parser=self.parser)

            self.prompt = PROMPT_REGISTRY["document_analysis"]

            self.log.info("DocumentAnalyzer initialized successfully.") 


        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException(e, sys)

    def analyze_document(self, document_text:str) -> dict:
        try:
            chain = self.prompt | self.llm | self.fixing_parser

            self.log.info("Metadata analysis chain initialized successfully.")
            
            response = chain.invoke({
                "format_instructions": self.fixing_parser.get_format_instructions(),
                "document_text": document_text
                }
            )

            self.log.info("Document Metadata analysis completed successfully.", response=response.keys())

            return response


        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException(e, sys)