# app/retrievers/base.py

from abc import ABC, abstractmethod


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, **kwargs) -> list:
        """
        Retrieve documents/snippets relevant to a query.
        Returns: List of dicts with at least:
          - type (e.g., "faiss", "chroma")
          - id (optional, for attribution)
          - snippet (text to show in UI)
          - title (optional)
          - url (optional)
        """
        pass
