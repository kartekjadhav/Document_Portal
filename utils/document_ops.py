from pathlib import Path
from typing import Iterable, List
from  langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
logger = CustomLogger().get_logger(__name__)

def load_documents(paths:Iterable[Path]):
    """Loads documents from a list of paths using appropriate loaders."""
    try:
        logger.info("Creating loaders.")
        docs:List[Document] = []
        for path in paths:
            if path.exists() and path.is_file():
                ext = path.suffix.lower()
                if ext == '.pdf':
                    loader = PyPDFLoader(str(path))
                elif ext == '.docx':
                    loader = Docx2txtLoader(str(path))
                elif ext == '.txt':
                    loader = TextLoader(str(path))
                else:
                    logger.warning(f"Extension {ext} not supported. Skipping {path}.")
                    continue
                docs.append(loader.load())
                logger.info("Loader created.", path=path, ext=ext)
        return docs
                    
    except Exception as e:
        logger.error("An error has occured while loading documents.")
        raise DocumentPortalException("Error occured while loading documents.", e)