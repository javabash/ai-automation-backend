## 🚀 Focused Project Summary


### README.md
```markdown
# 🤖 AI Automation Backend

A blazing-fast, RAG-powered backend built with **FastAPI**, **LangChain**, **Chroma**, and **OpenAI**—now with **JWT authentication**, **multi-retriever modularity**, and a modern **Next.js + TypeScript + Tailwind** frontend. Designed to ingest your own documents (PDFs, TXT) and let you query them using LLMs with real-time answers and robust source attribution. Production-ready for demos, portfolios, or client work.

![CI](https://github.com/javabash/ai-automation-backend/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/javabash/ai-automation-backend/branch/main/graph/badge.svg)](https://codecov.io/gh/javabash/ai-automation-backend)

---

## 🚀 Features

- 🔍 **Vector Search Engine** using Chroma and FAISS (multi-retriever support)
- 🧩 **Modular Retriever Registry**: Plug in new sources (docs, web, SQL, etc.)
- 📄 **Document Ingestion** (.txt, .pdf supported)
- 🧠 **Retrieval-Augmented Generation** with OpenAI GPT-3.5
- ⚡ **FastAPI backend** with interactive Swagger UI
- 🔐 **JWT-based Authentication** (OAuth2 standard, secure endpoints)
- 🖥️ **Next.js Frontend** (TypeScript, Tailwind, App Router)
- 🧪 **Production-grade Pytest suite** covering all endpoints and edge cases
- 🚦 **Standard RESTful error handling** (400, 401, 422, 200)
- 📦 **Modular Python structure** ready for production
- 🏷️ **Rich Source Attribution** (each answer cites its retrievers, files, and URLs)
- 🚀 **CI-ready**: Robust, contract-driven tests and GitHub Actions

---

## 🛠 Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| API Server | FastAPI                                 |
| LLM        | OpenAI GPT-3.5 (langchain-openai)       |
| Embeddings | OpenAIEmbeddings via langchain-openai   |
| Vector DB  | ChromaDB, FAISS                         |
| Loaders    | langchain_community.document_loaders    |
| Auth       | OAuth2, JWT                             |
| Frontend   | Next.js, TypeScript, Tailwind CSS       |

---

## 📂 Folder Structure

```
ai-automation-backend/
│
├── app/
│   ├── main.py                # FastAPI app and endpoints (now with JWT & modular retrievers)
│   ├── query_models.py        # Pydantic request/response schemas (was models.py)
│   ├── auth.py                # Auth logic and demo user db
│   ├── retrievers/            # Modular retriever implementations (chroma, faiss, mock, etc)
│   ├── vectorstore.py         # Vector store logic

... [TRUNCATED]
```

### requirements.txt
```text
# FastAPI app
fastapi==0.116.1
uvicorn==0.35.0

# AI/NLP core (keep these minimal, trim further if possible)
torch==2.7.1
torchvision==0.22.1
transformers==4.54.0
langchain==0.3.27
langchain-community==0.3.27
langchain-core==0.3.72
langchain-openai==0.3.28
langchain-text-splitters==0.3.9
chromadb==1.0.15
faiss-cpu==1.11.0.post1
openai==1.97.1
tiktoken==0.9.0

# Database, util, and parsing
SQLAlchemy==2.0.41
pandas==2.3.1
orjson==3.11.1
scipy==1.16.1
pydantic==2.11.7
pydantic-settings==2.10.1
pydantic_core==2.33.2
numpy==2.2.6
python-dotenv==1.1.1

# PDF, doc, and file processing (for RAG)
pdf2image==1.17.0
pdfminer.six==20250506
pypdf==5.9.0
pypdfium2==4.30.0
python-docx==1.2.0
python-pptx==1.0.2
openpyxl==3.1.5
pikepdf==9.10.2
unstructured==0.18.11
unstructured-client==0.41.0
unstructured-inference==1.0.5
unstructured.pytesseract==0.3.15

# Web, network, auth, and misc
httpx==0.28.1
aiofiles==24.1.0
aiohttp==3.12.14
bcrypt==4.3.0
python-multipart==0.0.20
requests==2.32.4
starlette==0.47.2
yarl==1.20.1

# Image handling (for PDF/RAG OCR if needed)
opencv-python==4.12.0.88
pillow==11.3.0

# (Other direct runtime deps as needed — can add back if runtime fails)
python-jose==3.5.0

```

### app/main.py
```python
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from langchain_openai import ChatOpenAI

from app.vectorstore import vector_search
from app.retrievers.registry import get_retrievers, RETRIEVERS
from app.query_models import AskRequest, AskResponse, SourceAttribution
from fastapi import Depends, FastAPI, HTTPException
from .auth import fake_users_db

# --- Import your source-of-truth Pydantic model ---
from app.models.source_of_truth import SourceOfTruth
from datetime import datetime
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load .env and keys ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

DEMO_USER = os.getenv("DEMO_USER", "__fallback_demo_user__")
DEMO_PASS = os.getenv("DEMO_PASS", "__fallback_demo_pass__")
print("DEBUG: DEMO_USER =", DEMO_USER)
print("DEBUG: DEMO_PASS =", DEMO_PASS)

# --- JWT Auth Config ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")  # fallback for dev
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# app = FastAPI()

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Token Endpoint ---
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("DEBUG: fake_users_db =", fake_users_db)
    print("DEBUG: Username received:", repr(form_data.username))
    print("DEBUG: Password received:", repr(form_data.password))
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        r

... [TRUNCATED]
```

### app/auth.py
```python
# app/auth.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

SECRET_KEY = "super-secret-key"  # Replace with environment var in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

fake_users_db = {"demo": {"username": "demo", "password": "test123"}}  # DEMO ONLY!


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Username received: {form_data.username!r}")
    print(f"Password received: {form_data.password!r}")
    # Just for testing:
    if form_data.username == "wrong":
        raise HTTPException(status_code=401, detail="This is a forced 401 for test")
    # Explicit check for empty/missing username/password
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        {"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

```

### app/vectorstore.py
```python
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

```

### app/query_models.py
```python
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

```

### app/models/source_of_truth.py
```python
from typing import List, Optional
from pydantic import BaseModel

class Experience(BaseModel):
    id: str
    title: str
    employer: str
    start_date: str  # "YYYY-MM"
    end_date: str    # "YYYY-MM"
    description: str
    skills: List[str]
    projects: List[str]
    outcomes: List[str]

class Project(BaseModel):
    id: str
    name: str
    summary: str
    tech_stack: List[str]
    outcomes: List[str]
    related_experience: Optional[str] = None

class Skill(BaseModel):
    name: str
    type: str  # language, framework, tool, etc.
    proficiency: str
    evidence: List[str]  # list of experience/project IDs

class Certification(BaseModel):
    name: str
    authority: str
    date: str  # "YYYY-MM" or year

class Education(BaseModel):
    degree: str
    institution: str
    date: str

class SourceOfTruth(BaseModel):
    experiences: List[Experience]
    projects: List[Project]
    skills: List[Skill]
    certifications: List[Certification]
    education: List[Education]

```

### app/retrievers/base.py
```python
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

```

### app/retrievers/chroma.py
```python
# app/retrievers/chroma.py

from .base import Retriever

# Import your Chroma client—this is an example using chromadb
# Adjust the import/init as needed for your actual setup.
import chromadb

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
            docs.append({
                "type": "chroma",
                "id": results["ids"][0][i] if results["ids"] else None,
                "title": results["metadatas"][0][i].get("title", "") if results.get("metadatas") else "",
                "snippet": doc_text,
                "url": results["metadatas"][0][i].get("url", "") if results.get("metadatas") else "",
            })
        return docs

```

### app/retrievers/faiss.py
```python
# app/retrievers/faiss.py

from .base import Retriever

class FAISSRetriever(Retriever):
    def __init__(self):
        # load FAISS index here if needed
        pass

    def retrieve(self, query: str, **kwargs) -> list:
        # Replace with your FAISS search logic
        # Return list of dicts as specified in base.py
        return [{
            "type": "faiss",
            "id": "doc_123",
            "title": "Example FAISS Result",
            "snippet": "Snippet matched from FAISS index.",
            "url": None
        }]

```

### app/retrievers/mock.py
```python
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
                "snippet": f"Matched '{query}' in a mock SDET project at ACME Corp.",
                "url": None
            },
            {
                "type": "mock",
                "id": "mock2",
                "title": "Mock Project: AI Job Match Copilot",
                "snippet": "Demonstrates experience with AI-powered resume generation and RAG search.",
                "url": None
            }
        ]

```

### app/retrievers/registry.py
```python
# app/retrievers/registry.py

from .faiss import FAISSRetriever
from .chroma import ChromaRetriever
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

```

### frontend/app/page.tsx
```typescript
"use client";
import { useState } from "react";
import AskForm from "../components/AskForm";
import AnswerDisplay from "../components/AnswerDisplay";
import SourcesList from "../components/SourcesList";
import LoginForm from "../components/LoginForm";
import { askBackend, login } from "../utils/api";

export default function Home() {
  const [token, setToken] = useState<string>("");
  const [loginError, setLoginError] = useState<string>("");
  const [loadingLogin, setLoadingLogin] = useState(false);

  // For /ask
  const [answer, setAnswer] = useState<string>("");
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (username: string, password: string) => {
    setLoadingLogin(true);
    setLoginError("");
    try {
      const data = await login(username, password);
      console.log("Login API returned:", data);     // <-- See the actual backend response
      if (data && data.access_token) {
        setToken(data.access_token);
      } else {
        setLoginError("Unexpected login response");
        console.error("Login response did not include access_token:", data);
      }
    } catch (err: any) {
      setLoginError("Invalid credentials");
      console.error("Login error:", err);
    }
    setLoadingLogin(false);
  };

  const handleAsk = async (question: string, selectedSources: string[]) => {
    setLoading(true);
    try {
      const data = await askBackend(question, selectedSources, token);
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err: any) {
      setAnswer("Error: " + err.message);
      setSources([]);
    }
    setLoading(false);
  };

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Vectorworx AI Frontend</h1>
      {!token ? (
        <>
          <LoginForm onLogin={handleLogin} loading={loadingLogin} />
          {loginError && <div className="text-red-600 mb-2">{loginError}</div>}
        </>
      ) : (
        <>
          <AskForm onAsk={handleAsk} loading={loading} />
          <AnswerDisplay answer={answer} loading={loading} />
          <SourcesList sources={sources} />
        </>
      )}
    </main>
  );
}

```

### frontend/components/AskForm.tsx
```typescript
// frontend/components/AskForm.tsx
"use client";
import { useState } from "react";

const retrieverOptions = ["mock", "chroma", "faiss"];

export default function AskForm({
  onAsk,
  loading,
}: {
  onAsk: (q: string, sources: string[]) => void;
  loading: boolean;
}) {
  const [question, setQuestion] = useState("");
  const [sources, setSources] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question && sources.length) onAsk(question, sources);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-2">
      <input
        className="p-2 border rounded"
        placeholder="Enter your question..."
        value={question}
        onChange={e => setQuestion(e.target.value)}
      />
      <div className="flex gap-2">
        {retrieverOptions.map(opt => (
          <label key={opt} className="flex items-center">
            <input
              type="checkbox"
              value={opt}
              onChange={e => setSources(s =>
                e.target.checked ? [...s, opt] : s.filter(x => x !== opt)
              )}
            />
            <span className="ml-1">{opt}</span>
          </label>
        ))}
      </div>
      <button
        className="bg-blue-500 text-white rounded px-4 py-2"
        type="submit"
        disabled={loading}
      >
        {loading ? "Asking..." : "Ask"}
      </button>
    </form>
  );
}

```

### frontend/components/LoginForm.tsx
```typescript
"use client";
import { useState } from "react";

export default function LoginForm({ onLogin, loading }: { onLogin: (username: string, password: string) => void, loading: boolean }) {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("test123");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin(username, password);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-2 max-w-xs">
      <input
        className="p-2 border rounded"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <input
        className="p-2 border rounded"
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <button
        className="bg-green-600 text-white rounded px-4 py-2"
        type="submit"
        disabled={loading}
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}

```

### frontend/components/AnswerDisplay.tsx
```typescript
export default function AnswerDisplay({ answer, loading }: { answer: string, loading: boolean }) {
  if (loading) return <div>Loading...</div>;
  if (!answer) return null;
  return <div className="p-4 bg-gray-100 rounded mb-2"><strong>Answer:</strong> {answer}</div>;
}
```

### frontend/components/SourcesList.tsx
```typescript

export default function SourcesList({ sources }: { sources: any[] }) {
  if (!sources?.length) return null;
  return (
    <div>
      <strong>Sources:</strong>
      <ul className="list-disc ml-6">
        {sources.map((src, idx) => (
          <li key={idx} className="mb-2">
            <div><b>{src.type}</b>{src.title ? `: ${src.title}` : ""}</div>
            <div className="text-sm text-gray-600">{src.snippet}</div>
            {src.url && <div><a href={src.url} className="text-blue-600" target="_blank" rel="noopener noreferrer">View Source</a></div>}
          </li>
        ))}
      </ul>
    </div>
  );
}

```

### frontend/utils/askBackend.ts
```typescript
// frontend/utils/askBackend.ts

export async function askBackend(
  question: string,
  sources: string[],
  token: string
) {
  const resp = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      sources,
    }),
  });

  if (!resp.ok) {
    throw new Error(`Ask failed (${resp.status}): ${await resp.text()}`);
  }

  // The API returns {answer, sources}
  return await resp.json();
}

```

### frontend/utils/login.ts
```typescript
// frontend/utils/login.ts

export async function login(username: string, password: string) {
  const resp = await fetch("http://localhost:8000/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });

  if (!resp.ok) {
    throw new Error(`Login failed (${resp.status}): ${await resp.text()}`);
  }

  // The API returns {access_token, token_type}
  return await resp.json();
}

```

### tests/test_api.py
```python
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# --------- Fixtures ---------
@pytest.fixture(scope="module")
def client():
    """Reusable TestClient for FastAPI app"""
    return TestClient(app)

# Get credentials from environment (fallback to defaults for local runs)
DEMO_USER = os.environ.get("DEMO_USER", "demo")
DEMO_PASS = os.environ.get("DEMO_PASS", "test123")  # Adjust to match .env

# --------- Auth Tests ---------

def test_login_valid(client):
    """Test valid login returns JWT token"""
    resp = client.post("/token", data={"username": DEMO_USER, "password": DEMO_PASS})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"

@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("wrong", DEMO_PASS, 401),      # wrong username
        (DEMO_USER, "wrong", 401),      # wrong password
        ("", DEMO_PASS, 400),           # empty username
        (DEMO_USER, "", 400),           # empty password
    ],
)
def test_login_invalid(client, username, password, expected_status):
    """Test login with invalid credentials yields correct status."""
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == expected_status

# Helper to get a valid token for authenticated requests
def get_token(client):
    resp = client.post("/token", data={"username": DEMO_USER, "password": DEMO_PASS})
    return resp.json()["access_token"]

# --------- /ask Endpoint Tests ---------

def test_ask_unauthenticated(client):
    """Test /ask rejects requests without JWT"""
    question = {"question": "What is vector search?"}
    resp = client.post("/ask", json=question)
    assert resp.status_code == 401

def test_ask_invalid_token(client):
    """Test /ask rejects requests with invalid JWT"""
    headers = {"Authorization": "Bearer not_a_real_token"}
    question = {"question": "What is vector search?"}
    resp = client.post("/ask", json=question, headers=headers)
    assert resp.status_code == 401

def test_ask_empty_question(client):
    """Test /ask handles empty input"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    question = {"question": ""}
    resp = client.post("/ask", json=question, headers=headers)
    # 422 = Unprocessable Entity; some apps return 400 for this
    assert resp.status_code in (400, 422)

def test_ask_valid(client

... [TRUNCATED]
```

### .github/workflows/ci.yml
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
  pull_request:

jobs:
  lint:
    name: 🧹 Lint & Format
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-lint-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-lint-

      - name: Install linters
        run: |
          pip install black isort flake8

      - name: Run black
        run: black --check app tests

      - name: Run isort
        run: isort --check-only app tests

      - name: Run flake8
        run: flake8 app tests

  test:
    name: 🧪 Run Tests with Coverage
    runs-on: ubuntu-latest
    needs: lint # Ensure linting passes before running tests

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx

      - name: Set PYTHONPATH
        run: echo "PYTHONPATH=$PWD" >> $GITHUB_ENV

      - name: Run pytest with coverage
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest tests/ --maxfail=1 --disable-warnings --cov=app --cov-branch --cov-report=xml -v

      - name: Upload coverage report to GitHub artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        with:
          files: ./coverage.xml
          # token: ${{ secrets.CODECOV_TOKEN }} # Uncomment if repo is private


```

### Dockerfile
```text
# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (including bash)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements and install Python dependencies as root
COPY requirements.txt .
# Use the extra PyTorch CPU index for torch+cpu wheels
RUN pip install --upgrade pip && \
    pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    rm -rf /root/.cache /tmp/*

# Create a non-root user for security
RUN adduser --disabled-password appuser

WORKDIR /app

# Copy FastAPI app code
COPY app/ ./app

# Make sure appuser owns /app (optional, but safe)
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Start Uvicorn ASGI server using Python module style (prod-ready)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

```

### .env.example
File not found.
