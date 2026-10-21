"""Regression tests for the generated PDF report.

The report used to print only the diagram captions and an empty Deciding
Factors table, so these tests decode the actual PDF bytes rather than trusting
the HTTP 200.
"""
import base64
import re
import zlib

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.schemas import FeatureVector, Prediction, Requirements
from app.services.architecture_service import generate_database
from app.services.diagram_service import build_architecture_diagram
from app.services.ml_service import get_ml_service

client = TestClient(app)

EDUCATION_REQUIREMENTS = Requirements(
    domain="online_education",
    actors=["student", "instructor", "admin"],
    modules=[
        "user_authentication_and_authorization",
        "course_management",
        "video_streaming",
        "quizzes_and_assessments",
        "assignment_submission_and_evaluation",
        "progress_tracking",
        "payment_processing",
        "notification_service",
        "ai_recommendation_engine",
        "analytics_dashboard",
    ],
    real_time=False,
    payment=True,
    external_integrations=["payment_gateway", "email_service", "video_hosting_cdn", "ai_service"],
    data_complexity="medium",
)

EDUCATION_FEATURES = FeatureVector(
    team_size=4,
    budget="low",
    expected_users="medium",
    number_of_roles=3,
    number_of_modules=10,
    real_time=False,
    payment=True,
    external_integrations=4,
    data_complexity="medium",
    availability="low",
    domain="online_education",
)

ANALYZE_PAYLOAD = {
    "description": (
        "An online learning platform where students enroll in courses, watch video "
        "lectures, take quizzes, submit assignments and track progress. Instructors "
        "create courses and grade work; the platform takes payments and sends email "
        "notifications. It starts at 5,000 users and must scale to 100,000 with a "
        "four-person team on a limited budget."
    ),
    "team_size": 4,
    "budget": "low",
    "expected_users": "medium",
    "availability": "low",
}


def _streams(pdf_bytes: bytes) -> list[str]:
    """Decode ReportLab's ASCII85+Flate content streams without extra packages."""
    decoded = []
    for _, body in re.findall(rb"(\d+) 0 obj(.*?)endobj", pdf_bytes, re.S):
        if b"stream" not in body:
            continue
        raw = body.split(b"stream", 1)[1]
        end = raw.find(b"~>")
        if end < 0:
            continue
        try:
            decoded.append(
                zlib.decompress(base64.a85decode(raw[:end].strip(), adobe=False)).decode("latin-1")
            )
        except Exception:
            continue
    return decoded


def _text(stream: str) -> str:
    return " ".join(match.group(1) for match in re.finditer(r"\((.*?)\)\s*Tj", stream))


def _all_text(streams: list[str]) -> str:
    return "\n".join(_text(stream) for stream in streams)


def _download_report() -> tuple[bytes, str]:
    analyze = client.post("/analyze", json=ANALYZE_PAYLOAD)
    assert analyze.status_code == 200
    report_id = analyze.json()["report_id"]

    response = client.get(f"/report/{report_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    return response.content, report_id


def test_report_contains_deciding_factors_and_probabilities():
    pdf, report_id = _download_report()
    streams = _streams(pdf)
    text = _all_text(streams)

    assert f"Report ID" in text and report_id in text

    # The section used to be rendered with a header row and no data rows.
    assert "Deciding Factors" in text
    assert "Number of modules" in text
    assert "Why it matters" in text

    # All three classes are scored, not just the winner.
    for architecture in ("Microservices", "Monolith", "Serverless"):
        assert architecture in text
    assert "model confidence" in text


def test_report_draws_both_diagrams():
    pdf, _ = _download_report()
    streams = _streams(pdf)

    architecture_page = next(s for s in streams if "Architecture Diagram" in _text(s))
    deployment_page = next(s for s in streams if "Deployment Diagram" in _text(s))

    # Node boxes and routed edge paths, not just a caption.
    assert len(re.findall(r"\bre\b", architecture_page)) >= 5
    assert len(re.findall(r"\bm\b", architecture_page)) >= 6
    assert "Client Application" in _text(architecture_page)
    assert "API Gateway" in _text(architecture_page)

    deployment_text = _text(deployment_page)
    assert "Web / Mobile Client" in deployment_text
    # Serverless deployments enter through an API gateway instead of a load balancer.
    assert "Load Balancer" in deployment_text or "API Gateway" in deployment_text


def test_top_factors_are_shares_of_total_importance():
    prediction = get_ml_service().predict(EDUCATION_FEATURES)

    assert prediction.top_factors
    assert all(0 < factor.importance < 1 for factor in prediction.top_factors)
    # Previously the top five were re-normalised to sum to exactly 1.0.
    assert sum(factor.importance for factor in prediction.top_factors) < 0.999


def test_schema_has_no_dangling_foreign_keys():
    database = generate_database(EDUCATION_REQUIREMENTS)
    table_names = {table.name for table in database.tables}

    for table in database.tables:
        for column in table.columns:
            if not column.endswith(" FK"):
                continue
            prefix = column[: -len("_id FK")]
            target = "".join(word.capitalize() for word in prefix.split("_"))
            assert target in table_names, f"{table.name}.{column} points at a missing table"

    # Domain tables, not a generic Order table with a dangling order_id.
    assert {"Course", "Enrollment", "Payment"} <= table_names


def test_microservice_diagram_uses_module_names():
    prediction = Prediction(
        architecture="Microservices",
        confidence=0.8,
        top_factors=[],
        alternatives=[],
    )
    database = generate_database(EDUCATION_REQUIREMENTS)

    diagram = build_architecture_diagram(prediction, database, None, EDUCATION_REQUIREMENTS)
    labels = {node.label for node in diagram.nodes}

    assert "Course Service" in labels
    assert "Assessment Service" in labels
    # Service names must come from modules, not from actor tables.
    assert "Student Service" not in labels
