import os
from typing import Dict, Optional, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

from src.document_ingestion.data_ingestion import (
    DocHandler,
    DocumentComparator,
    ChatIngestor,
    FaissManager,
    DocumentComparatorLLM
)
from src.document_analyser.document_analyser import DocumetAnalyzer
from src.document_comparer.document_comparer import DocumentComparer
from src.document_chat.retrieval import ConversationalRAG

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")

class FastAPIFileHandler:
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.file.name
    def get_buffer(self):
        return self._uf.read()

app = FastAPI(
    title="Document Portal API",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_crcedential=True
)

app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

def _read_pdf_via_handler(dh: DocHandler, path: str):
    text = dh.read_pdf(pdf_path=path)
    return text
    raise RuntimeError("DocHandler does not have read_pdf function.")

@app.get("/health")
def healthCheck() -> Dict[str, str]:
    return {"status": "ok", "service": "document_portal"}

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileHandler(file))
        text = _read_pdf_via_handler(dh, saved_path)
        analyzer = DocumetAnalyzer()
        response = analyzer.analyze_document(text)
        return JSONResponse(response, status_code=status.HTTP_201_CREATED)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
@app.post("/compare")
async def compare_documents(reference_file:UploadFile=File(...), actual_file:UploadFile=File(...)) -> Any:
    try:
        dc = DocumentComparator()
        reference_file_path, actual_file_path = dc.save_uploaded_files(FastAPIFileHandler(reference_file), FastAPIFileHandler(actual_file))

        combined_docs = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_docs)
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
    

@app.post("/chat/index")
async def chat_build_index(
        uploaded_files: List[UploadFile] = File(...),
        session_id: Optional[str] = Form(None),
        use_session_dirs: bool = Form(True),
        chunk_size: int = Form(1000),
        chunk_overlap: int = Form(200),
        k: int = Form(5)
    ):
    try:
        wrapped_files = [FastAPIFileHandler(file) for file in uploaded_files]
        ci = ChatIngestor(
            temp_base = UPLOAD_BASE,
            faiss_base = FAISS_BASE,
            use_session_dirs = use_session_dirs,
            session_id = session_id or None
        )

        ci.build_retriever(wrapped_files, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index creation failed: {str(e)}")
    

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        # Prepare FAISS index path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        # Initialize LCEL-style RAG pipeline
        rag = ConversationalRAG(session_id=session_id) #type: ignore
        rag.load_retriever_from_faiss(index_dir)

        # Optional: For now we pass empty chat history
        response = rag.invoke(question, chat_history=[])

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")