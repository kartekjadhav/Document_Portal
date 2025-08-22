import os
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from utils.model_loader import ModelLoader
from models.models import *


class DocumentAnalyzer:
    
    """
    A class to analyze documents using language models.
    Automatically logs operations and handles exceptions based on the session.
    """

    def __init__(self):
        pass

    def analyze_document(self):
        pass