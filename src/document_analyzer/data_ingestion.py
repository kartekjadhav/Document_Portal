import os
import sys
import fitz
import uuid
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException




class DocumentHandler:
    """
    A class to handle document operations such as reading and writing documents.
    Automatically logs operations and handles exceptions based on the session.
    """

    def __init__(self, data_dir=None, session_id=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv(
                "DATASTORAGE_PATH",
                os.path.join(os.getcwd(), "data", "document_analysis")
            )
            self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

            # Create base session directory
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)

            self.log.info(f"PDFHandler initialized", session_id=self.session_id, session_path=self.session_path)

        except Exception as e:
            self.log.error(f"Error initializing PDFHandler: {e}", session_id=self.session_id)
            raise DocumentPortalException(e, sys)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.file_name)
            # Check if format is .pdf only
            if not filename.endswith(".pdf"):
                self.log.error(f"Uploded file {filename} is not of .pdf format. Please upload a .pdf format file")
                raise DocumentPortalException(f"Uploded file {filename} is not of .pdf format. Please upload a .pdf format file", sys)

            save_path = os.path.join(self.session_path, filename)

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            self.log.info(f"PDF successfully saved to {save_path}", session_id=self.session_id)
            
            return save_path

        except Exception as e:
            self.log.error(f"Error saving PDF: {e}", session_id=self.session_id)
            raise DocumentPortalException(e, sys)

    def read_pdf(self, pdf_path:str) -> str:
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text()
                    text_chunks.append(f"\n ---- Page {page_num} ---- \n{text}")
            
            self.log.info(f"PDF successfully read from {pdf_path}", session_id=self.session_id, page_count=len(text_chunks))
            return "\n".join(text_chunks)

        except Exception as e:
            self.log.error(f"Error saving PDF: {e}", session_id=self.session_id)
            raise DocumentPortalException(e, sys)


if __name__ == "__main__":
    from pathlib import Path


    pdf_path = r"/home/shadyboy77/Kartek/LLMOPS/Document_Portal/data/document_analysis/NIPS-2017-attention-is-all-you-need-Paper.pdf"

    class DummyFile:
        """
        A dummy file class for testing.
        Mimics a uploaded file
        """
        def __init__(self, file_path):
            self.file_name = Path(file_path).name
            self._file_path = file_path  

        def getbuffer(self):
            return open(self._file_path, "rb").read()
    
    dummy_file = DummyFile(pdf_path)

    handler = DocumentHandler(session_id="test_session")

    try:
        saved_path = handler.save_pdf(dummy_file)
        print(handler.read_pdf(saved_path))
    except Exception as e:
        print(e)
