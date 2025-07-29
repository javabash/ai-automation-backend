import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from langchain_openai import ChatOpenAI

from app.models import QueryRequest, QueryResponse
from app.vectorstore import vector_search

from .auth import fake_users_db

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

app = FastAPI()


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
    print("Username (from form):", form_data.username)
    print("Password (from form):", form_data.password)
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# --- LLM Init ---
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)


# --- Protected RAG Endpoint ---
@app.post("/ask", response_model=QueryResponse)
async def ask_ai(request: QueryRequest, token_data=Depends(verify_token)):
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
        matched_docs=[d.page_content for d in docs],  # ✅ FIX: extract text
    )
