import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from langchain_openai import ChatOpenAI

# --- Import your source-of-truth Pydantic model ---
from app.models.source_of_truth import SourceOfTruth
from app.query_models import AskRequest, AskResponse, SourceAttribution
from app.retrievers.registry import RETRIEVERS, get_retrievers

from .auth import fake_users_db

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user["username"]})
    print(
        "DEBUG: About to return token:",
        {"access_token": access_token, "token_type": "bearer"},
    )

    return {"access_token": access_token, "token_type": "bearer"}


# --- LLM Init ---
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)


def generate_llm_explanation(job_description, obj, obj_type):
    # Build a tailored summary string
    if obj_type == "skill":
        summary = (
            f"Skill: {obj['name']}. Evidence: "
            + ", ".join(
                e["type"] + " - " + (e.get("title") or e.get("name"))
                for e in obj.get("evidence", [])
            )
            + "."
        )
    elif obj_type == "experience":
        summary = (
            f"Experience: {obj['title']} at {obj['employer']}. Outcomes: "
            + ", ".join(obj.get("outcomes", []))
            + "."
        )
    elif obj_type == "project":
        summary = f"Project: {obj['name']}. Summary: " + obj.get("summary", "") + "."
    else:
        summary = str(obj)

    prompt = (
        "Given the following job description and resume data, explain concisely "
        "and transparently why this {obj_type} is a strong match for the job. "
        "Do NOT restate the job description or skill, focus on the connection.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Candidate {obj_type.title()}:\n{summary}\n\n"
        "Your Explanation:"
    )

    # Make the LLM call
    result = llm.invoke(prompt)
    return result.content.strip()


# --- Modular Multi-Retriever /ask Endpoint ---
# Aggregates results from specified retrievers (FAISS, Chroma, Mock, etc.)
# Returns a synthesized answer with robust attribution for transparency and demo.
@app.post("/ask", response_model=AskResponse)
async def ask_ai(request: AskRequest, token_data=Depends(verify_token)):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty")

    retriever_names = request.sources or list(RETRIEVERS.keys())
    retrievers = get_retrievers(retriever_names)

    all_results = []
    for retriever in retrievers:
        all_results.extend(retriever.retrieve(request.question))

    if not all_results:
        return AskResponse(answer="No relevant information found.", sources=[])

    # Synthesize answer with LLM using context
    context = "\n".join([doc["snippet"] for doc in all_results])
    prompt = f"Context:\n{context}\n\nQuestion: {request.question}"
    result = llm.invoke(prompt)
    answer = result.content.strip()

    sources = [SourceAttribution(**doc) for doc in all_results]
    return AskResponse(answer=answer, sources=sources)


# --- Resume Source-of-Truth Endpoint ---
SOURCE_OF_TRUTH_PATH = "data/source_of_truth_seed.json"
try:
    with open(SOURCE_OF_TRUTH_PATH) as f:
        source_data = SourceOfTruth.model_validate_json(f.read())
except Exception as e:
    print(f"Could not load {SOURCE_OF_TRUTH_PATH}: {e}")
    source_data = None


@app.get("/resume/source", response_model=SourceOfTruth)
def get_source_of_truth():
    if source_data is None:
        raise HTTPException(status_code=500, detail="Source of truth not loaded")
    return source_data


# (Add Depends(verify_token) to /resume/source if you want to require login)


@app.post("/job/intake")
async def job_intake(job_description: str = Body(..., embed=True)):
    matches = []
    seen = set()

    # Skills
    for skill in source_data.skills:
        if skill.name.lower() in job_description.lower() and skill.name not in seen:
            seen.add(skill.name)
            evidence = []
            for evid in skill.evidence:
                exp = next((e for e in source_data.experiences if e.id == evid), None)
                proj = next((p for p in source_data.projects if p.id == evid), None)
                if exp:
                    evidence.append(
                        {
                            "type": "experience",
                            "title": exp.title,
                            "employer": exp.employer,
                            "links": getattr(exp, "links", []),
                        }
                    )
                elif proj:
                    evidence.append(
                        {
                            "type": "project",
                            "name": proj.name,
                            "links": getattr(proj, "links", []),
                        }
                    )
            match = {
                "type": "skill",
                "name": skill.name,
                "reason": (f"Matched because '{skill.name}' found in job description"),
                "evidence": evidence,
                "score": 2 + len(evidence),
            }
            # --- Add LLM explanation here ---
            match["llm_explanation"] = generate_llm_explanation(
                job_description, match, match["type"]
            )
            matches.append(match)

    # Experiences
    for exp in source_data.experiences:
        for skill in exp.skills:
            if skill.lower() in job_description.lower() and exp.title not in seen:
                seen.add(exp.title)
                year = int(exp.end_date.split("-")[0])
                recent = (datetime.now().year - year) < 3
                match = {
                    "type": "experience",
                    "title": exp.title,
                    "employer": exp.employer,
                    "reason": (
                        f"Matched because required skill '{skill}' found in job "
                        "description"
                    ),
                    "outcomes": exp.outcomes,
                    "links": getattr(exp, "links", []),
                    "recent": recent,
                    "score": 3 if recent else 2,
                }
                match["llm_explanation"] = generate_llm_explanation(
                    job_description, match, match["type"]
                )
                matches.append(match)
                break

    # Projects
    for proj in source_data.projects:
        tech_hit = any(
            tech.lower() in job_description.lower() for tech in proj.tech_stack
        )
        if tech_hit and proj.name not in seen:
            seen.add(proj.name)
            match = {
                "type": "project",
                "name": proj.name,
                "reason": (
                    "Matched because project uses tech stack "
                    f"{proj.tech_stack} found in job description"
                ),
                "summary": proj.summary,
                "links": getattr(proj, "links", []),
                "score": 2,
            }
            match["llm_explanation"] = generate_llm_explanation(
                job_description, match, match["type"]
            )
            matches.append(match)

    # Sort matches by score (descending)
    matches = sorted(matches, key=lambda m: m["score"], reverse=True)

    return {"matches": matches, "job_description": job_description}
