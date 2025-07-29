# 🤖 AI Automation Backend

A blazing-fast, RAG-powered backend built with **FastAPI**, **LangChain**, **Chroma**, and **OpenAI**. Designed to ingest your own documents (PDFs, TXT) and let you query them using LLMs with real-time answers.

![CI](https://github.com/javabash/ai-automation-backend/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/javabash/ai-automation-backend/branch/main/graph/badge.svg)](https://codecov.io/gh/javabash/ai-automation-backend)

---

## 🚀 Features

- 🔍 **Vector Search Engine** using Chroma
- 📄 **Document Ingestion** (.txt, .pdf supported)
- 🧠 **Retrieval-Augmented Generation** with OpenAI GPT-3.5
- ⚡ **FastAPI backend** with interactive Swagger UI
- 🔐 **Environment-based API key security**
- 🧪 **Production-grade Pytest suite** covering all endpoints and edge cases
- 🚦 **Standard RESTful error handling** (400, 401, 422, 200)
- 📦 **Modular Python structure** ready for production

---

## 🛠 Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| API Server | FastAPI                                 |
| LLM        | OpenAI GPT-3.5                          |
| Embeddings | OpenAIEmbeddings via langchain-openai   |
| Vector DB  | ChromaDB                                |
| Loaders    | langchain_community.document_loaders    |

---

## 📂 Folder Structure

```
ai-automation-backend/
│
├── app/
│   ├── main.py           # FastAPI app and endpoints
│   ├── models.py         # Pydantic request/response schemas
│   ├── vectorstore.py    # Vector store logic
│   └── docs/             # Drop your .txt and .pdf files here
│
├── tests/                # 🧪 Pytest API contract tests
├── .env                  # Contains your OPENAI_API_KEY
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

1. **Clone the repo**
  ```bash
  git clone https://github.com/javabash/ai-automation-backend.git
  cd ai-automation-backend
  ```

2. **Set up a virtual environment**
  ```bash
  python -m venv .venv
  ```
  Activate it:

  **Windows**
  ```bash
  .venv\Scripts\activate
  ```

  **Mac/Linux**
  ```bash
  source .venv/bin/activate
  ```

3. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

4. **Create a `.env` file in the root**

  Add your OpenAI API key:
  ```ini
  OPENAI_API_KEY=your_openai_key_here
  ```

5. **Start the server**
  ```bash
  uvicorn app.main:app --reload
  ```

6. **Open your browser**

  Visit: [http://localhost:8000/docs](http://localhost:8000/docs)  
  Use the Swagger UI to query your documents.

---

## 🧪 API Testing & Quality

All endpoints are covered by a robust Pytest suite:

- Auth (happy/negative paths)
- Permissions (future-proofed for roles)
- RAG/LLM endpoints (happy/edge/error cases)
- Error handling (bad login, missing/empty inputs, etc.)

Test suite checks status codes and API contracts:

- **401 Unauthorized** for invalid login
- **400 Bad Request** for missing/blank fields
- **422 Unprocessable Entity** for empty questions
- **200 OK** for successful calls

**CI/CD ready:**

- Tests pass locally and in GitHub Actions
- Every change must be testable, reproducible, and contract-aligned

---

## 🏃‍♂️ Run Tests

```bash
pytest -v tests/
```

---

## 📥 Adding Documents

Just drop `.txt` or `.pdf` files into the `app/docs/` directory. The app will:

- Automatically detect and load them
- Chunk the text using `RecursiveCharacterTextSplitter`
- Convert chunks to vector embeddings
- Store them in Chroma for similarity search

No manual indexing required.

---

## ❓ Ask Your Data

**Example query:**
```json
{
  "question": "What is a vector database and why is it useful?"
}
```

The app will:

1. Search your document collection for relevant chunks
2. Insert those chunks as context into a prompt
3. Send the prompt to OpenAI
4. Return an intelligent answer + the source context

**Example response:**
```json
{
  "answer": "Vector databases improve performance for AI by enabling similarity search and handling high-dimensional data efficiently.",
  "matched_docs": [
  "Beginner’s Guide to Vector Databases -AI by Hand",
  "FastAPI Type Hints and Swagger UI Integration"
  ]
}
```

---

## 🚦 Error Handling & API Contract

All API endpoints follow standard REST conventions:

| Status Code | Scenario                                 |
|-------------|------------------------------------------|
| 200         | Success                                  |
| 400         | Missing required fields (e.g. blank login)|
| 401         | Invalid credentials or unauthorized      |
| 422         | Invalid input (e.g. empty question)      |

Any contract change will cause tests to fail—preventing accidental regressions.

All errors return a clear JSON message:
```json
{ "detail": "Error message here" }
```

---

## 🧱 Built For Expansion

This is just the backend. Future upgrades could include:

- Web frontend (React, Svelte, etc.)
- File upload via API
- Streamed token-by-token responses
- Fine-tuned models or local LLMs (e.g. Ollama, LM Studio)
- Multi-user support with authentication
- Metadata tagging and filters

---

## 🧠 Author

**Philip GeLinas**  
AI-Enhanced SDET & Automation Engineer  
GitHub: [@javabash](https://github.com/javabash)

---

## 📘 Acknowledgments

- LangChain
- Chroma
- OpenAI
- FastAPI

---

## ⚖️ License

**MIT** — do whatever you want, just don't forget to build cool stuff.

---
