import sys
from datetime import datetime
from uuid import uuid4
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentIngestion:
    def __init__(self, base_dir:str="data/document_compare", session_id=None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.sesssion_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
        self.session_path = self.base_dir / self.sesssion_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentComparator initialized successfully.") 
        

    def save_uploaded_file(self, reference_file, actual_file):
        """
        Save the uploaded file to a specific directory.
        """
        try:
            self.log.info("Starting uploading of provided files.")

            reference_file_path = self.session_path / reference_file.name
            actual_file_path = self.session_path / actual_file.name

            if reference_file_path.suffix != ".pdf" or actual_file_path.suffix != ".pdf":
                raise ValueError("Only PDF files are allowed.")
            
            with open(reference_file_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(actual_file_path, "wb") as f:
                f.write(actual_file.getbuffer())
            
            self.log.info("Successfully uploaded files.", reference_file_path=str(reference_file_path), actual_file_path=str(reference_file_path))

            return reference_file_path, actual_file_path

        except Exception as e:
            self.log.error("Error in saving uploaded file", error=str(e))
            DocumentPortalException("Error in saving uploaded file", sys)

    def read_pdf(self, file:Path):
        """
        Read the PDF file and return the text content.
        """
        try:
            self.log.info("Starting the reading of file", file={file})
            with fitz.open(file) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"File is encrypted, {file}", sys)
                docs = []
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text().strip()
                    docs.append(f"\n\n-------Page {page_num}--------\n\n{text}\n\n")
                self.log.info(f"PDF successfully read.", file={file})
                return "\n".join(docs)

        except Exception as e:
            self.log.error("Error in reading pdf file", error=str(e))
            DocumentPortalException("Error in reading pdf file", sys)

    # def delete_existing_files(self):
    #     """
    #     Delete the existing files at base dir.
    #     """
    #     try:
    #         self.log.info("Starting the cleanup of existing files.")
    #         for file in self.base_dir.iterdir():
    #             if file.is_file():
    #                 file.unlink()
    #                 self.log.info("Deleted existing file", file=str(file))
    #         self.log.info("Existing files deleted successfully.")
    #     except Exception as e:
    #         self.log.error("Error in deleting uploaded file", error=str(e))
    #         DocumentPortalException("Error in deleting uploaded file", sys)

    def combine_documents(self):
        """
        Combine the uploaded files text and return.
        """
        try:
            self.log.info("Starting combining the documents.")
            docs_text = []
            combine_docs = {}
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix == ".pdf":
                    combine_docs[file.name] = self.read_pdf(file)

            for filename, data in combine_docs.items():
                docs_text.append(f"Document: {filename}\n\n{data}\n\n")
            
            self.log.info("Successfully combined the documents and returning now.")
            return "".join(docs_text)

        except Exception as e:
            self.log.error("Error occuered while combining the files")
            DocumentPortalException("Error occuered while combining the files", sys)

    
    def clean_old_file(self, keep_latest:int=3):
        """
        Clean old files. Keep only the latest N sessions.
        """
        try:
            self.log.info("Starting cleaning old files.")
            session_folders = sorted(
                [folder for folder in self.base_dir.iterdir() if folder.is_dir()],
                reverse=True
            )

            if len(session_folders) > keep_latest:
                for folder in session_folders[keep_latest:]:
                    for file in folder.iterdir():
                        if file.is_file():
                            file.unlink()
                            self.log.info(f"Deleted old file.", file=str(file))
                    folder.rmdir()
                    self.log.info(f"Deleted old folder.", folder=str(folder))

            self.log.info("Old files cleaned successfully.")
        except Exception as e:
            self.log.error("Error in cleaning old files", error=str(e))
            DocumentPortalException("Error in cleaning old files", sys)

