# app/models.py

from typing import List

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    matched_docs: List[str]
