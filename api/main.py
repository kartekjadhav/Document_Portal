from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse

import os
from typing import Dict, Any, List, Optional


from src.document_ingestion.data_ingestion import (
    ChatIngestor,
    DocHandler,
    DocumentComparator,
    FaissManager
)
from src.document_analyser.document_analyser import DocumetAnalyzer
from src.document_comparer.document_comparer import DocumentComparer
from src.document_chat.retrieval import ConversationalRAG

app = FastAPI(title="Document Portal API", version="0.1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credential=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


## server static files and templates
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "document_portal"}

class FastApiFileAdapter:
    """
    Adapt FastAPI UploadFile -> .name, .getbuffer
    """
    def __init__(self, uf: UploadFile) -> None:
        self._uf = uf
        self.name = uf.filename
    def getbuffer(self):
        self._uf.file.seek(0)
        return self._uf.file.read()

def _read_pdf_via_handler(file: DocHandler, save_path:str) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {e}")

@app.post("/analyze")
def analyse_document(file: UploadFile = File(...)) -> Any:
    try:
        dh = DocHandler()
        save_path = dh.save_pdf(FastApiFileAdapter(file))
        text = _read_pdf_via_handler(dh, save_path)
        result = DocumetAnalyzer().analyze_document(text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/compare")
async def compare_documents(reference_file: UploadFile = File(...), actual_file: UploadFile = File(...)) -> Any:
    try:
        dc = DocumentComparator()
        reference_file_path, actual_file_path = dc.save_uploaded_files(FastApiFileAdapter(reference_file)), dc.save_uploaded_files(FastApiFileAdapter(actual_file))
        combined_text = dc.combine_documents()
        comp = DocumentComparer()
        df = comp.compare_docs(combined_docs=combined_text)
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id} 

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comarison failed: {e}")
    
@app.post("/chat/index")
async def build_chat_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5)
    ) -> Any:
    try:
        wrapped = [FastApiFileAdapter(file) for file in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None
        )
        ci.build_retriever(wrapped, chunk_size, chunk_overlap, k)
        return {"session_id": session_id, "k":k, "use_session_dir": use_session_dirs}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    
@app.post("/chat/query")
async def query_chat_index(
    question: str = Form(...),
    session_id: str = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5)
    ) -> Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when using use_session_dirs=True")
        
        # Prepare FAISS index path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=400, detail=f"FAISS index not found at {index_dir}")
        
        # Initialize LCEL-style RAG pipeline
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir)

        # Invoke RAG
        response = rag.invoke(user_input=question, chat_history=[])

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
    






# uvicorn main:app --reload