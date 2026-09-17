import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    # It might fail if startup didn't complete yet, but with TestClient it runs the events if properly invoked
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_troubleshoot_api():
    with TestClient(app) as client:
        response = client.post("/v1/troubleshoot", json={"query": "battery dies fast"})
        assert response.status_code == 200
        data = response.json()
        assert "contexts" in data
        assert len(data["contexts"]) > 0
        
        goal = data["contexts"][0]
        assert "goal" in goal
        assert "Battery Troubleshooting" in goal["goal"]
