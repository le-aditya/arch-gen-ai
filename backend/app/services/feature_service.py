"""Converts LLM-extracted requirements + user input into the ML feature vector (PRD section 8).

Every field here must be knowable before the application exists -- no post-launch
signals (traffic, commits, deployed servers) are used.
"""
from app.schemas.schemas import FeatureVector, ProjectInput, Requirements


def extract_features(project_input: ProjectInput, requirements: Requirements) -> FeatureVector:
    return FeatureVector(
        team_size=project_input.team_size,
        budget=project_input.budget,
        expected_users=project_input.expected_users,
        number_of_roles=len(requirements.actors),
        number_of_modules=len(requirements.modules),
        real_time=requirements.real_time,
        payment=requirements.payment,
        external_integrations=len(requirements.external_integrations),
        data_complexity=requirements.data_complexity,
        availability=project_input.availability,
        domain=requirements.domain,
    )
