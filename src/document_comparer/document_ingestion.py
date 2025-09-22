import os
import sys
import fitz
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException



class DocumentIngestion:
    """
    Document Ingestion class for Document Comparer. 
    Contains save_pdf, read_pdf, combine_documents, and remove_existing_documents methods.
    """
    
    def __init__(self, base_dir="data/document_comparer", session_id=None):
        self.logger = CustomLogger().get_logger(__name__)
        try:
            self.base_dir = Path(base_dir)
            self.session_id = session_id or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:6]}"

            self.session_path = self.base_dir / self.session_id
            self.session_path.mkdir(parents=True, exist_ok=True)

            self.logger.info("DocumentIngestion has been initialized for Document Comparer", session_id=self.session_id)
        
        except Exception as e:
            self.logger.error("An error has occured while initialising DocumentIngestion.")
            raise DocumentPortalException(e, sys)
        
    def save_pdf(self, reference_file, actual_file):
        """
        Save the reference and actual pdf files.
        """
        try:
            self.logger.info("Starting to save the pdf files.", reference_file=reference_file.file, actual_file=actual_file.file)
            
            reference_file_path =  self.session_path / reference_file.file
            actual_file_path = self.session_path / actual_file.file

            if reference_file_path.suffix != ".pdf" or actual_file_path.suffix != ".pdf":
                self.logger.error("Uploaded file is not of PDF type. Please upload PDF file.", reference_file=reference_file.file, actual_file=actual_file.file)
                raise DocumentPortalException("Uploaded file is not of PDF type. Please upload PDF file.", sys)
            

            with open(reference_file_path, "wb") as f:
                f.write(reference_file.get_buffer())

            with open(actual_file_path, "wb") as f:
                f.write(actual_file.get_buffer())

            self.logger.info("PDF files have been saved successfully.", reference_file=reference_file.file, actual_file=actual_file.file)

            return reference_file_path, actual_file_path

        except Exception as e:
            self.logger.error("An error has occured while saving the pdf files.", reference_file=reference_file, actual_file=actual_file)
            raise DocumentPortalException(e, sys)

    def read_pdf(self, save_path:Path) -> str:
        """
        Read the pdf files.
        """
        try:
            self.logger.info("Starting to read the pdf files.", path=save_path)

            with fitz.open(save_path) as docs:
                if docs.is_encrypted:
                    self.logger.error("PDF file is encrypted. Please decrypt the file.", path=save_path)
                    raise DocumentPortalException("PDF file is encrypted. Please decrypt the file.", sys)
                chunks = []

                for page_num, page in enumerate(docs):
                    text = page.get_text()
                    chunks.append(f"\n\n-------Page no. {page_num}-------\n\n{text}")

                self.logger.info("PDF file has been read successfully.", path=save_path)
                return "\n".join(chunks)

        except Exception as e:
            self.logger.error("An error has occured while reading the pdf files.")
            raise DocumentPortalException(e, sys)

    def combine_documents(self):
        """
        Combine the documents.
        """
        try:
            combine_docs = {}

            for file in self.session_path.iterdir():
                if file.is_file() and file.suffix == ".pdf":
                    combine_docs[file.name] = self.read_pdf(file)

            self.logger.info("Documents have been combined successfully.")
            return "\n\n".join([f"\n\n-------Document: {key}-------\n\n{value}"  for key, value in combine_docs.items()])

        except Exception as e:
            self.logger.error("An error has occured while combining the documents.")
            raise DocumentPortalException(e, sys)

    def clean_old_file(self, keep_latest:int=3):
        """
        Remove the existing documents.
        """
        try:
            self.logger.info("Starting to remove the existing documents.")
            dirs = sorted([d for d in self.base_dir.iterdir() if d.is_dir()], reverse=True)

            if len(dirs) > keep_latest:
                for sub_dir in dirs[keep_latest:]:
                    for file in sub_dir.iterdir():
                        if file.is_file():
                            self.logger.info("Removing existing document.", file=file)
                            file.unlink()
                            self.logger.info("Document has been removed successfully.", file=file)
                    sub_dir.rmdir()
                    self.logger.info("Directory has been removed successfully.", directory=sub_dir)
            self.logger.info("Existing documents have been removed successfully.")

        except Exception as e:
            self.logger.error("An error has occured while removing the existing documents.")
            raise DocumentPortalException(e, sys)