from fastapi import APIRouter, HTTPException

from app.schemas.schemas import PredictionRequest, PredictionResponse
from app.services.ml_service import get_ml_service

router = APIRouter()


@router.post("/predict-architecture", response_model=PredictionResponse)
def predict_architecture(payload: PredictionRequest):
    try:
        service = get_ml_service()
        prediction = service.predict(payload.features)
    except Exception:
        raise HTTPException(status_code=503, detail="Architecture prediction unavailable.")
    return PredictionResponse(
        architecture=prediction.architecture,
        confidence=prediction.confidence,
        top_factors=prediction.top_factors,
    )
