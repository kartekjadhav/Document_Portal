# from pydantic import BaseModel, Field, RootModel
# from typing import List, Optional
# from enum import Enum

from pydantic import BaseModel, Field, RootModel
from typing import List
from enum import Enum

class Metadata(BaseModel):
    Title: str
    Author: str
    Summary: List[str] = Field(default_factory=List, description="Summary of document.")
    PageCount: str
    Language: str
    Publication: str
    DateCreated: str
    LastModified: str
    Sentimentation: str

class ChangeFormat(BaseModel):
    Page: str
    Changes: str


class Summary(RootModel[list[ChangeFormat]]):
    pass


class PromptType(str, Enum):
    DOCUMENT_ANALYZER = "document_analyzer_prompt"
    DOCUMENT_COMPARER = "document_comparer_prompt"
    CONTEXTUALIZE_QUESTION = "contextualize_prompt"
    CONTEXT_QA = "context_qa_prompt"

