import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentComparator:
    def __init__(self, base_dir="docs"):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentComparator initialized successfully.") 
        

    def save_uploaded_file(self, reference_file, actual_file):
        """
        Save the uploaded file to a specific directory.
        """
        try:
            self.log("Starting uploading of provided files.")
            self.delete_existing_files()

            reference_file_path = self.base_dir / reference_file
            actual_file_path = self.base_dir / actual_file

            if not reference_file_path.endswith(".pdf") or actual_file_path.endswith(".pdf"):
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

    def delete_existing_files(self):
        """
        Delete the existing files at base dir.
        """
        try:
            self.log.info("Starting the cleanup of existing files.")
            for file in self.base_dir.iterdir():
                if file.is_file():
                    file.unlink()
                    self.log.info("Deleted existing file: {file}")
            self.log.info("Existing files deleted successfully.")
        except Exception as e:
            self.log.error("Error in deleting uploaded file", error=str(e))
            DocumentPortalException("Error in deleting uploaded file", sys)

    def combine_documents(self):
        """
        Combine the uploaded files text and return.
        """
        try:
            self.log.info("Starting combining the documents.")
            docs_text = []
            combine_docs = {}
            for file in sorted(self.base_dir.iterdir()):
                if file.is_file() and file.suffix == ".pdf":
                    combine_docs[file.name] = self.read_pdf(file)

            for filename, data in combine_docs.items():
                docs_text.append(f"Document: {filename}\n\n{data}\n\n")
            
            self.log.info("Successfully combined the documents and returning now.")
            return "".join(docs_text)

        except Exception as e:
            self.log.error("Error occuered while combining the files")
            DocumentPortalException("Error occuered while combining the files", sys)