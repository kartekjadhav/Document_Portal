from enum import Enum
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional

class MetaData(BaseModel):
    Title: str
    Author: str
    Summary: List[str] = Field(default_factory=list, description="Summary of the document")
    DateCreated: str
    LatdModeified: str
    Publisher: str
    Language: str
    PageCount: int
    SentimentTone: str


class ChangeFormat(BaseModel):
    Page: str
    Changes: str


class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass


class PromptType(str, Enum):
    DOCUMENT_ANALYSIS = "document_analysis_prompt"
    DOCUMENT_COMPARISION = "document_comparison_prompt"
    CONTEXTUALIZE_QUESTION = "contextualize_prompt"
    CONNTEXT_QA = "context_qa"