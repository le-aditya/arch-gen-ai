from fastapi import APIRouter, HTTPException

from app.schemas.schemas import RequirementsExtractRequest, RequirementsExtractResponse
from app.services.llm_service import extract_requirements_safe

router = APIRouter()


@router.post("/extract-requirements", response_model=RequirementsExtractResponse)
def extract_requirements(payload: RequirementsExtractRequest):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="Please provide an application description.")
    try:
        requirements = extract_requirements_safe(payload.description)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to extract requirements. Please try again.")
    return RequirementsExtractResponse(requirements=requirements)
