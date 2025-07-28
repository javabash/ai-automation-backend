from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from app.vectorstore import vector_search
from app.models import QueryRequest, QueryResponse
from dotenv import load_dotenv
import os
 
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=api_key
)

# 🔍 Ask endpoint using real Document chunks
@app.post("/ask", response_model=QueryResponse)
async def ask_ai(request: QueryRequest):
    docs = vector_search(request.question)

    print("\n\n🔍 MATCHED DOCS DEBUG:")
    for i, d in enumerate(docs):
        print(f"\n--- Chunk #{i+1} ---")
        print(d.page_content[:500])  # ✅ FIX: use .page_content

    context = "\n".join([d.page_content for d in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {request.question}"
    result = llm.invoke(prompt)

    return QueryResponse(
        answer=result.content,
        matched_docs=[d.page_content for d in docs]  # ✅ FIX: extract text
    )

