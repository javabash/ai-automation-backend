# app/retrievers/chroma.py

# Import your Chroma client—this is an example using chromadb
# Adjust the import/init as needed for your actual setup.
import chromadb

from .base import Retriever


class ChromaRetriever(Retriever):
    def __init__(self):
        # Connect to Chroma (example: local DB)
        self.client = chromadb.PersistentClient(path="./app/chroma_db/")
        self.collection = self.client.get_or_create_collection("default")

    def retrieve(self, query: str, **kwargs) -> list:
        # Chroma query (simplified demo—update for your schema)
        results = self.collection.query(query_texts=[query], n_results=3)
        # Assume results["documents"], results["ids"], results["metadatas"]
        docs = []
        for i, doc_text in enumerate(results["documents"][0]):
            docs.append(
                {
                    "type": "chroma",
                    "id": results["ids"][0][i] if results["ids"] else None,
                    "title": (
                        results["metadatas"][0][i].get("title", "")
                        if results.get("metadatas")
                        else ""
                    ),
                    "snippet": doc_text,
                    "url": (
                        results["metadatas"][0][i].get("url", "")
                        if results.get("metadatas")
                        else ""
                    ),
                }
            )
        return docs
