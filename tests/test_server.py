import pytest
from fastapi.testclient import TestClient
from llmforge.server import app

client = TestClient(app)

def test_main_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "LLMForge Lab Dashboard" in response.text

def test_human_review_ui():
    response = client.get("/review")
    assert response.status_code == 200
    assert "Human Review Workspace" in response.text

def test_review_api_workflow():
    # 1. Fetch pending reviews
    res = client.get("/api/reviews")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1

    item_id = items[0]["id"]

    # 2. Submit decision ACCEPT
    dec_res = client.post("/api/reviews/decision", json={"item_id": item_id, "decision": "ACCEPT"})
    assert dec_res.status_code == 200
    assert dec_res.json()["new_status"] == "ACCEPT"

    # 3. Verify item is removed from pending reviews list
    res_after = client.get("/api/reviews")
    items_after = res_after.json()
    assert all(i["id"] != item_id for i in items_after)
