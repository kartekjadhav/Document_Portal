import sys
from pathlib import Path
from uuid import uuid4
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader


class SingleDocumentChatIngestion:
    
    def __init__(self, data_dir:str="data/single_document_chat", faiss_dir:str ="faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)

            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.loader = ModelLoader()

            self.log.info("SingleDocumentChatIngestion initialized successfully.", extra={"data_dir": str(self.data_dir), "faiss_dir": str(self.faiss_dir)})

        except Exception as e:
            self.log.error(f"Error initializing SingleDocumentChatIngestion: {e}")
            raise DocumentPortalException(e, sys)
    
    def ingest_files(self, uploaded_files):
        try:
            documents = []
            for file in uploaded_files:
                unique_filename = f"datetime.now().strftime('%Y%M%d_%H%M%S)_{uuid4().hex[:6]}_{file.name}"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(file.read())

                self.log.info(f"File saved.", file=str(file.name), path=str(temp_path))

                loader = PyPDFLoader(str(unique_filename))
                temp_doc = loader.load()
                documents.extend(temp_doc)

            self.log.info(f"Total PDF's loaded", count={len(documents)})  
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error ingesting files: {e}")
            raise DocumentPortalException(e, sys)
    
    def _create_retriever(self, documents):
        try:
            # Chunking the documents
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(documents)
            self.log.info("Chunking of documents completed", chunks_length=len(chunks))

            # Creating vectore store
            embeddings = self.loader.load_embbeddings()
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            self.log.info("Created vectorestor Successfully.", vectorestore=vectorstore)

            # Save FAISS locally
            FAISS.save_local(str(self.data_dir))
            self.log.info("FAISS index saved locally.", path=str(self.faiss_dir))

            # Creating Retriever
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriever created successfully.", retriever_type=str(type(retriever)))

            return retriever
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentPortalException(e, sys)
    