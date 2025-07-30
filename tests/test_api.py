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
        ("wrong", DEMO_PASS, 401),  # wrong username
        (DEMO_USER, "wrong", 401),  # wrong password
        ("", DEMO_PASS, 400),  # empty username
        (DEMO_USER, "", 400),  # empty password
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


def test_ask_valid(client):
    """Test authenticated /ask returns expected structure (default retrievers)"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    question = {"question": "What is vector search?"}
    resp = client.post("/ask", json=question, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    if data["sources"]:
        for s in data["sources"]:
            assert "type" in s
            assert "snippet" in s


def test_ask_multi_retriever(client):
    """Test /ask with multiple sources param"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "question": "Show my Python automation experience.",
        "sources": ["mock", "chroma"],  # Use retrievers you have
    }
    resp = client.post("/ask", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0


# --------- Parameterized Edge/Role/Perf (Stubs) ---------


@pytest.mark.parametrize("role", ["demo", "admin", "readonly"])
def test_roles_future(client, role):
    """Stub for role-based access (expand when roles are implemented)"""
    pass


@pytest.mark.performance
def test_ask_latency(client):
    """Basic latency/perf check for /ask endpoint (optional)"""
    import time

    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    question = {"question": "Quick?"}
    start = time.time()
    client.post("/ask", json=question, headers=headers)
    elapsed = time.time() - start
    assert elapsed < 2.0  # Fail if response takes longer than 2 seconds
