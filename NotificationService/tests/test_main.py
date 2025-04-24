from fastapi.testclient import TestClient
import pytest
from app.main import app

# Create test client
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_send_notification():
    notification_data = {
        "user_id": 1,
        "message": "Test notification message"
    }
    response = client.post("/api/notifications", json=notification_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["notification"]["user_id"] == 1
    assert data["notification"]["message"] == "Test notification message"