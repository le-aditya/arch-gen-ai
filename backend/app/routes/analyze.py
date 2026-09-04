import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.orm import Prediction as PredictionModel
from app.models.orm import Project, Report, Requirement
from app.schemas.schemas import AnalyzeResponse, ProjectInput
from app.services.architecture_service import generate_apis, generate_database, generate_tech_stack
from app.services.diagram_service import generate_diagrams
from app.services.feature_service import extract_features
from app.services.llm_service import extract_requirements_safe
from app.services.ml_service import get_ml_service

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: ProjectInput, db: Session = Depends(get_db)):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="Please provide an application description.")

    try:
        requirements = extract_requirements_safe(payload.description)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to extract requirements. Please try again.")

    features = extract_features(payload, requirements)

    try:
        ml_service = get_ml_service()
        prediction = ml_service.predict(features)
    except Exception:
        raise HTTPException(status_code=503, detail="Architecture prediction unavailable.")

    tech_stack = generate_tech_stack(requirements, prediction, budget=payload.budget)
    database = generate_database(requirements)
    apis = generate_apis(requirements)
    diagrams = generate_diagrams(prediction, database, tech_stack)

    project = Project(
        description=payload.description,
        team_size=payload.team_size,
        budget=payload.budget,
        expected_users=payload.expected_users,
        availability=payload.availability,
    )
    db.add(project)
    db.flush()

    db.add(Requirement(project_id=project.project_id, requirement_data=requirements.model_dump_json()))
    db.add(PredictionModel(
        project_id=project.project_id,
        architecture=prediction.architecture,
        confidence=prediction.confidence,
        model_version="random_forest_v1",
    ))

    report_id = f"rpt_{uuid.uuid4().hex[:10]}"
    db.add(Report(report_id=report_id, project_id=project.project_id))
    db.commit()

    return AnalyzeResponse(
        project_id=project.project_id,
        report_id=report_id,
        requirements=requirements,
        prediction=prediction,
        tech_stack=tech_stack,
        database=database,
        apis=apis,
        diagrams=diagrams,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
