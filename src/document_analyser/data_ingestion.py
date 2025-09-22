import os
import sys
from datetime import datetime
from uuid import uuid4
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
import fitz
from pathlib import Path

class DocumentHandler:
    def __init__(self, data_dir:str="data", session_id=None):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            data_dir_path = Path(r"C:\Users\hp\OneDrive\Documents\Kartek\LLMOPS\Document_Portal") / data_dir / "document_analyzer"
            self.data_dir = os.getenv("DATA_STORAGE_PATH", data_dir_path)

            self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}"

            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)

            self.logger.info("DocumentHandler has been initialized for Document Analyzer", session_id=self.session_id)

        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentHandler for Document Analyzer.")
            raise DocumentPortalException(e, sys)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.endswith(".pdf"):
                self.logger.error(f"Uploaded file {filename} is not of PDF type. Please upload PDF file.", session_id = self.session_id)
                raise DocumentPortalException("Uploaded file {filename} is not of PDF type. Please upload PDF file.", sys)

            save_path = os.path.join(self.session_path, filename)

            with open(save_path, "wb") as f:
                f.write(uploaded_file.get_buffer())

            self.logger.info(f"File {filename} has been save successfully.", path=save_path)

            return save_path

        except Exception as e:
            self.logger.error("An error has occured while saving the pdf file.")
            raise DocumentPortalException(e,  sys)

    def read_pdf(self, save_path):
        try:
            chunks = []

            with fitz.open(save_path) as docs:
                for page_num, page in enumerate(docs):
                    text = page.get_text()
                    chunks.append(f"\n\n-------Page no. {page_num}-------\n\n{text}")
            
            self.logger.info("PDF file has been read successfully.", path=save_path)
            return "\n".join(chunks)

        except Exception as e:
            self.logger.error("An error has occured while reading the pdf file.")
            raise DocumentPortalException(e,  sys)