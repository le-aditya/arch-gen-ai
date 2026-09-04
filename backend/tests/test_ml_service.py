from app.schemas.schemas import FeatureVector
from app.services.ml_service import get_ml_service


def test_predict_returns_valid_architecture_and_confidence():
    service = get_ml_service()
    features = FeatureVector(
        team_size=4,
        budget="low",
        expected_users="medium",
        number_of_roles=4,
        number_of_modules=6,
        real_time=True,
        payment=True,
        external_integrations=3,
        data_complexity="high",
        availability="high",
        domain="food_delivery",
    )

    prediction = service.predict(features)

    assert prediction.architecture in {"Monolith", "Microservices", "Serverless"}
    assert 0.0 <= prediction.confidence <= 1.0
    assert len(prediction.top_factors) > 0
    for factor in prediction.top_factors:
        assert factor.importance >= 0


def test_predict_handles_unseen_domain_gracefully():
    service = get_ml_service()
    features = FeatureVector(
        team_size=2,
        budget="low",
        expected_users="low",
        number_of_roles=1,
        number_of_modules=2,
        real_time=False,
        payment=False,
        external_integrations=0,
        data_complexity="low",
        availability="low",
        domain="totally_unseen_domain_xyz",
    )

    prediction = service.predict(features)

    assert prediction.architecture in {"Monolith", "Microservices", "Serverless"}
