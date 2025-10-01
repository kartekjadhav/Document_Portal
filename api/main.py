from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse

from typing import Dict, Any

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

@app.post("/analyze")
def analyse_document(file: UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/compare")
async def compare_documents(reference_file: UploadFile = File(...), actual_file: UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comarison failed: {e}")
    
@app.post("/chat/index")
async def build_chat_index(file: UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    
@app.post("/chat/query")
async def query_chat_index(query: str = Form(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
    






# uvicorn main:app --reload