import sys
from dotenv import load_dotenv
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from models.models import *
import pandas as pd


class DocumentCompareLLM():
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentCompareLLM successfully initialised.")

    def compare_documents(self, combined_docs:str) -> pd.DataFrame:
        """
        Compare two documents in a structured way.
        """
        try:
            response = self.chain.invoke({
                "format_instructions": self.fixing_parser.get_format_instructions(),
                "document_text_combined": combined_docs
            })

            return self._format_response(response)

        except Exception as e:
            self.log.error("Error in comparing documents", error=str(e))
            DocumentPortalException("An error occured while comparing documents.", sys)

    def _format_response(self, response_parsed) -> pd.DataFrame:
        """
        Format the response from the LLM in a structured way.
        """
        try:
            return pd.DataFrame(response_parsed)
        except Exception as e:
            self.log.error("Error in formatting the response", error=str(e))
            DocumentPortalException("An error occured while formatting the response.", sys)