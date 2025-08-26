import os
import sys
from datetime import datetime
from uuid import uuid4
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

    def save_uploaded_file(self, reference_file, actual_file):
        """
        Save the uploaded file to a specific directory.
        """
        try:
            self.delete_existing_files()
            
            reference_file_path = self.base_dir / reference_file
            actual_file_path = self.base_dir / actual_file

            if not reference_file.endswith(".pdf") or not actual_file.endwith(".pdf"):
                raise ValueError("Only PDF files are allowed.")

            with open(reference_file_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(actual_file_path, "wb") as f:
                f.write(actual_file.getbuffer())

            self.log.info("Successuly saved uploaded files.", reference_file_path={str(reference_file_path)}, actual_file_path={str(actual_file_path)})
            return reference_file_path, actual_file_path

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
                return "\n".join(doc_text)

        except Exception as e:
            self.log.error("Error in reading uploaded file", error=str(e))
            DocumentPortalException("Error in reading uploaded file", sys)

    def delete_existing_files(self):
        """
        Delete the existing files at specific paths.
        """
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                        self.log.info(f"Deleted existing file: {file}")
                self.log.info("Existing files deleted successfully.")
        except Exception as e:
            self.log.error("Error in deleting uploaded file", error=str(e))
            DocumentPortalException("Error in deleting uploaded file", sys)

    
    def conbine_documents(self):
        try:
            docs_part  = []
            content = {}
            for file in self.base_dir.iterdir():
                if file.is_file() and file.suffix == ".pdf":
                    content[file.name] = self.read_pdf(file)
            
            for filename, data in content.items():
                docs_part.append(f"Document: {filename}\n\n{data}\n\n")
            
            combined_text = "\n".join(docs_part)
            return combined_text


        except Exception as e:
            self.log.error("Error occuered while combining the files")
            DocumentPortalException("Error occuered while combining the files", sys)