"""Threshold rule-based baseline (PRD section 17A). Hand-written, not learned."""


def predict_baseline(row: dict) -> str:
    """row has the raw (unencoded) feature dict, e.g. one row of the dataset."""
    scale = row["expected_users"]
    team_size = row["team_size"]
    modules = row["number_of_modules"]
    budget = row["budget"]
    availability = row["availability"]

    if scale == "high" and availability == "high":
        return "Microservices"
    if team_size <= 3 and budget == "low" and modules <= 6:
        return "Serverless"
    return "Monolith"
