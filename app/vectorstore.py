import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ✅ Load .env if not loaded already
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 📁 Paths
DOCS_PATH = "app/docs"
VECTOR_DB_PATH = "app/chroma_db"

# 🔤 Embedding model
embeddings = OpenAIEmbeddings()


# 📄 Load and split documents
def load_documents():
    docs = []
    for filename in os.listdir(DOCS_PATH):
        full_path = os.path.join(DOCS_PATH, filename)

        if filename.endswith(".txt"):
            loader = TextLoader(full_path, encoding="utf-8")
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(full_path)
        else:
            continue

        docs.extend(loader.load())
    return docs


# ✂️ Split text into chunks
def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)


# 📥 Load and store in Chroma
documents = load_documents()
chunks = split_documents(documents)

vectorstore = Chroma.from_documents(
    chunks, embeddings, persist_directory=VECTOR_DB_PATH
)


# 🔍 Vector search returns full Document objects
def vector_search(query):
    return vectorstore.similarity_search(query, k=3)
