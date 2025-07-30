# app/retrievers/mock.py

from .base import Retriever


class MockRetriever(Retriever):
    def retrieve(self, query: str, **kwargs) -> list:
        # Always return a couple of dummy results
        return [
            {
                "type": "mock",
                "id": "mock1",
                "title": "Mock Experience: Python Automation",
                "snippet": (
                    f"Matched '{query}' in a mock SDET project at " "ACME Corp."
                ),
                "url": None,
            },
            {
                "type": "mock",
                "id": "mock2",
                "title": "Mock Project: AI Job Match Copilot",
                "snippet": (
                    "Demonstrates experience with AI-powered resume "
                    "generation and RAG search."
                ),
                "url": None,
            },
        ]
