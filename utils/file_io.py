from pathlib import Path
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Iterable, List, Optional

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

logger = CustomLogger().get_logger(__name__)
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def generate_session_id(prefix: str = "session") -> str:
    ist = ZoneInfo('Asia/Kolkata')
    return f"{prefix}_{datetime.now(ist).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

def save_uploaded_files(uploaded_files:Iterable, target_dir:Path) -> List[Path]:
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        save:List[Path] = []
        for file in uploaded_files:
            name = getattr(file, 'name', 'file')
            ext = Path(name).suffix.lower()

            if ext not in SUPPORTED_EXTENSIONS:
                raise DocumentPortalException(f'{ext} not in Supported extensions.')
                continue

            fname = f"{uuid4().hex[:8]}{ext}"
            out = target_dir / fname
            with open(out, "wb") as f:
                if hasattr(file, 'read'):
                    f.write(file.read())
                elif hasattr(file, 'getbuffer'):
                    f.write(file.getbuffer())
            save.append(out)
            logger.info("File saved", name=name, ext=ext, fname=fname, out=out)
        return save
    except Exception as e:
        logger.error("An error has occured while saving files.")
        raise DocumentPortalException("Error occured while saving files.", e)

