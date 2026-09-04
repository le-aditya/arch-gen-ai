from app.schemas.schemas import ProjectInput, Requirements
from app.services.feature_service import extract_features


def test_extract_features_matches_requirements_counts():
    project_input = ProjectInput(
        description="A food delivery platform",
        team_size=4,
        budget="low",
        expected_users="medium",
        availability="high",
    )
    requirements = Requirements(
        domain="food_delivery",
        actors=["customer", "restaurant", "delivery_partner", "admin"],
        modules=["registration", "browsing", "ordering", "payment", "tracking", "notifications"],
        real_time=True,
        payment=True,
        external_integrations=["maps", "payment_gateway", "sms"],
        data_complexity="high",
    )

    features = extract_features(project_input, requirements)

    assert features.team_size == 4
    assert features.budget == "low"
    assert features.expected_users == "medium"
    assert features.availability == "high"
    assert features.number_of_roles == 4
    assert features.number_of_modules == 6
    assert features.real_time is True
    assert features.payment is True
    assert features.external_integrations == 3
    assert features.data_complexity == "high"
    assert features.domain == "food_delivery"
