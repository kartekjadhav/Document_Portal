import os
import sys
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from logger.custom_logger import CustomLogger
from exception.custom_exception_archive import DocumentPortalException
from utils.model_loader import ModelLoader
from models.models import Metadata
from prompts.prompt_library import PROMPT_REGISTRY
from models.models import PromptType

class DocumetAnalyzer:
    def __init__(self):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.prompt = PROMPT_REGISTRY.get(PromptType.DOCUMENT_ANALYZER)
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            self.logger.info("DocumetAnalyzer initialised successfully.")

        except Exception as e:
            self.logger.error("An error has occured while initialising DocumetAnalyzer.")
            raise DocumentPortalException(e, sys)
    
    def analyze_document(self, docs):
        try:
            self.logger.info("Starting to analyze the document.")

            chain = self.prompt | self.llm | self.fixing_parser
            response = chain.invoke({
                "format_instructions": self.fixing_parser.get_format_instructions(),
                "document_text": docs
                })
            
            self.logger.info("Document analysis has been completed.", keys=response.keys())
            return response
        except Exception as e:
            self.logger.error("An error has occured while analyzing the document.")
            raise DocumentPortalException(e, sys)
        