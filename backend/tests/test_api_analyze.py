import os
import tempfile

os.environ.setdefault("GEMINI_API_KEY", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_analyze_end_to_end_food_delivery():
    payload = {
        "description": (
            "I want to build an online food delivery platform where customers can "
            "browse restaurants, order food, make payments and track delivery in real-time."
        ),
        "team_size": 4,
        "budget": "low",
        "expected_users": "medium",
        "availability": "high",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "requirements" in data
    assert "prediction" in data
    assert data["prediction"]["architecture"] in {"Monolith", "Microservices", "Serverless"}
    assert 0 <= data["prediction"]["confidence"] <= 1
    assert "tech_stack" in data
    assert "database" in data
    assert "apis" in data
    assert "diagrams" in data
    assert data["report_id"].startswith("rpt_")


def test_analyze_rejects_empty_description():
    payload = {
        "description": "",
        "team_size": 2,
        "budget": "low",
        "expected_users": "low",
        "availability": "low",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code in (400, 422)


def test_report_download_after_analyze():
    payload = {
        "description": "A small internal admin dashboard for a two-person team.",
        "team_size": 2,
        "budget": "low",
        "expected_users": "low",
        "availability": "low",
    }
    analyze_response = client.post("/analyze", json=payload)
    report_id = analyze_response.json()["report_id"]

    report_response = client.get(f"/report/{report_id}")

    assert report_response.status_code == 200
    assert report_response.headers["content-type"] == "application/pdf"
