# app/retrievers/registry.py

from .chroma import ChromaRetriever
from .faiss import FAISSRetriever
from .mock import MockRetriever

# Registry pattern: simple dict mapping names to retriever instances
RETRIEVERS = {
    "faiss": FAISSRetriever(),
    "chroma": ChromaRetriever(),
    "mock": MockRetriever(),
}


def get_retrievers(names):
    """Fetch retrievers by name; return list of retriever instances"""
    return [RETRIEVERS[name] for name in names if name in RETRIEVERS]
