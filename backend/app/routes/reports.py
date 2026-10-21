import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.orm import Report
from app.schemas.schemas import ProjectInput, Requirements
from app.services.architecture_service import generate_apis, generate_database, generate_tech_stack
from app.services.diagram_service import generate_diagrams
from app.services.feature_service import extract_features
from app.services.ml_service import get_ml_service
from app.services.report_service import generate_pdf

router = APIRouter()


@router.get("/report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    project = report.project
    if project is None or project.requirement is None:
        raise HTTPException(status_code=404, detail="Report data is incomplete.")

    requirements = Requirements(**json.loads(project.requirement.requirement_data))

    # Only architecture and confidence are persisted, so the full prediction
    # (feature importances and per-class probabilities) is rebuilt from the
    # stored project inputs. The classifier is deterministic, so this reproduces
    # the decision that was shown in the app and keeps the PDF's "Deciding
    # Factors" section filled in.
    project_input = ProjectInput(
        description=project.description,
        team_size=project.team_size,
        budget=project.budget,
        expected_users=project.expected_users,
        availability=project.availability,
    )
    features = extract_features(project_input, requirements)
    prediction = get_ml_service().predict(features)

    stored = project.prediction
    model_version = stored.model_version if stored is not None else "random_forest_v2"

    tech_stack = generate_tech_stack(requirements, prediction, budget=project.budget)
    database = generate_database(requirements)
    apis = generate_apis(requirements)
    diagrams = generate_diagrams(prediction, database, tech_stack, requirements)

    # Regenerate on every request so a report downloaded after a generator fix
    # is never served from a stale file on disk.
    pdf_path = generate_pdf(
        report_id=report_id,
        description=project.description,
        requirements=requirements,
        prediction=prediction,
        tech_stack=tech_stack,
        database=database,
        apis=apis,
        diagrams=diagrams,
        model_version=model_version,
        features=features,
        budget=project.budget,
        created_at=report.created_at,
    )
    if report.report_path != str(pdf_path):
        report.report_path = str(pdf_path)
        db.commit()

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{report_id}.pdf")
