# import pytest  # Removed unused import
from fastapi.testclient import TestClient

from app.main import app  # Import your actual FastAPI app


def test_login_and_ask():
    # Create a test client instance for the FastAPI app.
    # This allows us to make HTTP requests (POST/GET) as if we were a real
    # user/client.
    client = TestClient(app)

    # 1️⃣ Try the /ask endpoint WITHOUT a token: tests your security. /ask
    # should reject unauthenticated requests.
    question = {"question": "What is vector search?"}
    resp = client.post("/ask", json=question)
    assert resp.status_code == 401  # 401 Unauthorized is expected

    # 2️⃣ Login to get a JWT
    # Simulate a user logging in with demo credentials for an access token.
    login_data = {
        "username": "demo",  # should match DEMO_USER from .env
        "password": "test123",  # should match DEMO_PASS from .env
    }
    resp = client.post("/token", data=login_data)
    assert resp.status_code == 200  # Login must succeed (200 OK)
    token = resp.json()["access_token"]  # Extract JWT token from response

    # 3️⃣ Now call /ask WITH the token (authenticated request): simulates a real
    # logged-in user querying your AI endpoint.
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/ask", json=question, headers=headers)
    assert resp.status_code == 200  # Should succeed for authenticated requests

    # 4️⃣ Check API returns expected structure
    data = resp.json()
    assert "answer" in data  # LLM-generated answer present
    assert "matched_docs" in data  # Doc chunks used for context present
