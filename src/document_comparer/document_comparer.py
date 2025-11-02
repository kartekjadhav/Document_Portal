import pandas as pd

from logger.custom_logger import CustomLogger
from exception.custom_exception import  DocumentPortalException
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompts.prompt_library import PROMPT_REGISTRY
from models.models import Summary, PromptType

class DocumentComparer:
    def __init__(self):
        """
        Class to compare two PDFs.
        """
        try:
            self.logger = CustomLogger().get_logger(__name__)

            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            
            self.parser = JsonOutputParser(pydantic_object=Summary)
            self.fixing_parser = OutputFixingParser.from_llm(llm=self.llm, parser=self.parser)
            
            self.prompt = PROMPT_REGISTRY.get(PromptType.DOCUMENT_COMPARER)

            self.chain = self.prompt | self.llm | self.fixing_parser
            
            self.logger.info("DocumentComparer initialised successfully.")
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentComparer.")
            raise DocumentPortalException("Error occured while initialising DocumentComparer.", e) from e

    def compare_docs(self, combined_docs:str) -> pd.DataFrame:
        """
        Compare two PDFs and return the results in a pandas dataframe.
        """
        try:
            response = self.chain.invoke({
                "format_instructions": self.fixing_parser.get_format_instructions(),
                "combined_documents": combined_docs
            })
            
            self.logger.info("Document comparison has been completed.")
            return self._format_docs(response)
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentComparer.")
            raise DocumentPortalException("Error occured while initialising DocumentComparer.", e) from e

    def _format_docs(self, response) -> pd.DataFrame:
        """
        Format the response into a pandas dataframe.
        """
        try:
            return pd.DataFrame(response)
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentComparer.")
            raise DocumentPortalException("Error occured while initialising DocumentComparer.", e) from e