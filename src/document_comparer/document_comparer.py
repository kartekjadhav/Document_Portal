import os
import sys
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from exception.custom_exception_archive import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompts.prompt_library import PROMPT_REGISTRY
from models.models import Summary, PromptType
from utils.model_loader import ModelLoader
import pandas as pd


class DocumentComparer:
    """
    Class to compare two PDFs.
    """
    def __init__(self):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.parser = JsonOutputParser(pydantic_object=Summary)
            self.fixing_parser = OutputFixingParser.from_llm(llm=self.llm, parser=self.parser)

            self.prompt = PROMPT_REGISTRY.get(PromptType.DOCUMENT_COMPARER)

            self.chain = self.prompt | self.llm | self.fixing_parser

            self.logger.info("DocumentComparer initialised successfully.")

        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentComparer.")
            raise DocumentPortalException(e, sys)
    
    def compare_docs(self, combined_docs:str):
        """
        Compare two PDFs.
        """
        try:
            self.logger.info("Starting to compare the documents.")

            response = self.chain.invoke({
                "format_instructions": self.fixing_parser.get_format_instructions(),
                "combined_documents": combined_docs
            })

            return self._format_response(response)

        except Exception as e:
            self.logger.error("An error has occured while comparing the documents.")
            raise DocumentPortalException(e, sys)
        
    
    def _format_response(self, response) -> pd.DataFrame:
        """
        Format the response into a pandas dataframe.
        """
        try:
            return pd.DataFrame(response)

        except Exception as e:
            self.logger.error("An error has occured while formatting the response.")
            raise DocumentPortalException(e, sys)