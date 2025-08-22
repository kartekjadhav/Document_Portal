from pydantic import BaseModel, Field
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