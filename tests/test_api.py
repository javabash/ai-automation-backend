from http import client
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_login_and_ask():
    client = TestClient(app)

    # Try /ask with no token (should fail)
    question = {"question": "What is vector search?"}
    resp = client.post("/ask", json=question)
    assert resp.status_code == 401

    # Login for JWT
    login_data = {
        "username": "demo",
        "password": "test123"
    }
    resp = client.post("/token", data=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # Now /ask with token
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/ask", json=question, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "matched_docs" in data
