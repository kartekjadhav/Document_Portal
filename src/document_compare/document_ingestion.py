import os
import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException



class DocumentComparator:
    def __init__(self, base_dir):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentComparator initialized successfully.")

    def save_uploaded_file(self):
        """
        Save the uploaded file to a specific directory.
        """
        try:
            pass
        except Exception as e:
            self.log.error("Error in saving uploaded file", error=str(e))
            DocumentPortalException("Error in saving uploaded file", sys)

    def read_pdf(self, pdf_path:Path) -> str:
        """
        Read the PDF file and return the text content.
        """
        try:
            self.log.info("Reading uploaded file")
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"File is encrypted, {pdf_path}", sys)
                doc_text = []
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text().strip()
                    if text:
                        doc_text.append(f"\n\n-------Page {page_num}-------\n\n{text}")
                self.log.info(f"PDF successfully read from {pdf_path}")
                return "".join(doc_text)

        except Exception as e:
            self.log.error("Error in reading uploaded file", error=str(e))
            DocumentPortalException("Error in reading uploaded file", sys)

    def delete_existing_files(self):
        """
        Delete the existing files at specific paths.
        """
        try:
            pass
        except Exception as e:
            self.log.error("Error in deleting uploaded file", error=str(e))
            DocumentPortalException("Error in deleting uploaded file", sys)