from __future__ import annotations
import os
import sys
import json
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict, Any

import fitz
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

class FaissManager:
    def __init__(self, index_dir:Path, model_loader: Optional[ModelLoader]) -> None:
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta: Dict[str, Any] = {"rows": {}}

        if self.meta_path.exists():
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}}
            except:
                self._meta = {"rows": {}}

        self.model_loader = model_loader or ModelLoader()
        self.emb = self.model_loader.load_embedding()
        self.vs: Optional[FAISS] = None
    def _exists(self) -> bool:
        return (self.index_dir / "index.faiss").exists() and (self.index_dir / "index.pkl").exists() 

    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")


    @staticmethod
    def _fingerprint(text:str, md: Dict[str, Any]) -> str:
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")
        if src is not None:
            return f"{src}::{"" if rid is None else rid}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def add_documents(self, docs: List[Document]):
        if self.vs is None:
            raise RuntimeError("Call load_or_create() first before adding documents.")

        new_docs: List[Document] = []

        for d in docs:
            key = self._fingerprint(d.page_content, d.metadata or {})
            if key in self._meta["rows"]:
                continue
            self._meta[key] = True
            new_docs.append(d)
        
        if new_docs:
            self.vs.add_documents(new_docs)
            self.vs.save_local(str(self.index_dir))
            self._save_meta()

        return new_docs

    def load_or_create(self):
        if self._exists():
            self.vs = FAISS.load_local(
                folder_path=str(self.index_dir), 
                embeddings=self.emb,
                allow_dangerous_deserialization=True
            )
            return self.vs



class DocHandler:
    def __init__(self):
        pass

    def save_pdf(self):
        pass

    def read_pdf(self):
        pass    
        
    


class DocumentComparator:
    def __init__(self):
        pass

    def save_uploaded_files(self):
        pass

    def combine_documents(self):
        pass

    def read_pdf(self):
        pass

    def clean_old_session(self):
        pass


class ChatIngestor:
    def __init__(self):
        pass
    def _resolve_dir(self):
        pass
    def _split(self):
        pass
    def build_retriever(self):
        pass