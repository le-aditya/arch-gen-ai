from fastapi import APIRouter

from app.schemas.schemas import GenerationRequest, GenerationResponse
from app.services.architecture_service import generate_apis, generate_database, generate_tech_stack
from app.services.diagram_service import generate_diagrams

router = APIRouter()


@router.post("/generate-architecture", response_model=GenerationResponse)
def generate_architecture(payload: GenerationRequest):
    requirements = payload.requirements
    prediction = payload.prediction

    tech_stack = generate_tech_stack(requirements, prediction, budget="medium")
    database = generate_database(requirements)
    apis = generate_apis(requirements)
    diagrams = generate_diagrams(prediction, database, tech_stack, requirements)

    return GenerationResponse(tech_stack=tech_stack, database=database, apis=apis, diagrams=diagrams)
