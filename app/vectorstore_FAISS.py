# app/vectorstore.py

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ✅ Load environment (if not already loaded elsewhere)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize OpenAI embedding model
embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# ✅ Load all .txt files from docs folder
loader = DirectoryLoader("app/docs", glob="**/*.txt", loader_cls=TextLoader)
raw_docs = loader.load()

# ✅ Split documents into manageable chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs = splitter.split_documents(raw_docs)

# ✅ Create or reuse a FAISS vector store
db = FAISS.from_documents(docs, embeddings)


# ✅ Simple vector search function
def vector_search(query: str) -> list[str]:
    results = db.similarity_search(query, k=3)
    return [doc.page_content for doc in results]
