# app/vectorstore.py

# Temporary dummy data
DOCUMENTS = [
    "LangChain helps you build apps with LLMs using modular components.",
    "FastAPI is a modern web framework for building APIs with Python 3.6+.",
    "ChatOpenAI is a wrapper for OpenAI's chat models within LangChain.",
    "Vector search allows semantic search using document embeddings."
]

def vector_search(query: str) -> list[str]:
    """
    Simulates a vector search by returning all documents that contain any word from the query.
    Replace this with real embedding + similarity logic later.
    """
    query_words = set(query.lower().split())
    matches = [
        doc for doc in DOCUMENTS
        if query_words & set(doc.lower().split())
    ]
    return matches if matches else ["No relevant documents found."]
