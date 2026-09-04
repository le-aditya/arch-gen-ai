import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.orm import Report
from app.schemas.schemas import Prediction, Requirements
from app.services.architecture_service import generate_apis, generate_database, generate_tech_stack
from app.services.diagram_service import generate_diagrams
from app.services.report_service import generate_pdf

router = APIRouter()


@router.get("/report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    pdf_path = Path(report.report_path) if report.report_path else None
    if pdf_path is None or not pdf_path.exists():
        project = report.project
        requirement = project.requirement
        prediction_row = project.prediction

        requirements = Requirements(**json.loads(requirement.requirement_data))
        # top_factors aren't persisted (only architecture/confidence are); the PDF
        # report omits the per-factor breakdown on regeneration.
        prediction = Prediction(
            architecture=prediction_row.architecture,
            confidence=prediction_row.confidence,
            top_factors=[],
        )

        tech_stack = generate_tech_stack(requirements, prediction, budget=project.budget)
        database = generate_database(requirements)
        apis = generate_apis(requirements)
        diagrams = generate_diagrams(prediction, database, tech_stack)

        pdf_path = generate_pdf(
            report_id=report_id,
            description=project.description,
            requirements=requirements,
            prediction=prediction,
            tech_stack=tech_stack,
            database=database,
            apis=apis,
            diagrams=diagrams,
            model_version=prediction_row.model_version,
        )
        report.report_path = str(pdf_path)
        db.commit()

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{report_id}.pdf")
