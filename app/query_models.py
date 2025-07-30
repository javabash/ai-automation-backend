from typing import List, Optional

from pydantic import BaseModel


class SourceAttribution(BaseModel):
    type: str
    id: Optional[str] = None
    title: Optional[str] = None
    snippet: str
    url: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    sources: Optional[List[str]] = None  # If not provided, use all retrievers


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceAttribution]


# Optionally, keep legacy models for backwards compatibility:
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    matched_docs: List[str]
