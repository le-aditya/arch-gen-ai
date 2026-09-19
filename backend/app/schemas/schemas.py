"""Pydantic models mirroring the PRD's JSON contracts."""
from typing import Literal
from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    description: str = Field(min_length=1)
    team_size: int = Field(ge=1, le=200)
    budget: Literal["low", "medium", "high"]
    expected_users: Literal["low", "medium", "high"]
    availability: Literal["low", "medium", "high"]


class RequirementsExtractRequest(BaseModel):
    description: str = Field(min_length=1)


class Requirements(BaseModel):
    domain: str
    actors: list[str]
    modules: list[str]
    real_time: bool
    payment: bool
    external_integrations: list[str]
    data_complexity: Literal["low", "medium", "high"]


class RequirementsExtractResponse(BaseModel):
    requirements: Requirements


class FeatureVector(BaseModel):
    team_size: int
    budget: Literal["low", "medium", "high"]
    expected_users: Literal["low", "medium", "high"]
    number_of_roles: int
    number_of_modules: int
    real_time: bool
    payment: bool
    external_integrations: int
    data_complexity: Literal["low", "medium", "high"]
    availability: Literal["low", "medium", "high"]
    domain: str


class PredictionRequest(BaseModel):
    features: FeatureVector


class TopFactor(BaseModel):
    name: str
    importance: float


class ClassProbability(BaseModel):
    """One architecture style and the probability the classifier assigned it."""

    architecture: str
    probability: float


class Prediction(BaseModel):
    architecture: Literal["Monolith", "Microservices", "Serverless"]
    confidence: float
    top_factors: list[TopFactor]
    # Every class the model scored, highest first -- the winning class is the
    # first entry, so `confidence` is `alternatives[0].probability`.
    alternatives: list[ClassProbability] = []


class PredictionResponse(BaseModel):
    architecture: str
    confidence: float
    top_factors: list[TopFactor]
    alternatives: list[ClassProbability] = []


class GenerationRequest(BaseModel):
    requirements: Requirements
    prediction: Prediction


class TechStack(BaseModel):
    frontend: list[str]
    backend: list[str]
    database: list[str]
    messaging: list[str]
    infrastructure: list[str]


class DbTable(BaseModel):
    name: str
    columns: list[str]


class Database(BaseModel):
    tables: list[DbTable]


class ApiEndpoint(BaseModel):
    method: str
    path: str
    purpose: str


class DiagramNode(BaseModel):
    id: str
    label: str
    kind: Literal["client", "gateway", "service", "database", "queue", "infra"]


class DiagramEdge(BaseModel):
    source: str
    target: str


class Diagram(BaseModel):
    caption: str
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]


class Diagrams(BaseModel):
    architecture: Diagram
    deployment: Diagram


class GenerationResponse(BaseModel):
    tech_stack: TechStack
    database: Database
    apis: list[ApiEndpoint]
    diagrams: Diagrams


class AnalyzeResponse(BaseModel):
    project_id: int
    report_id: str
    requirements: Requirements
    prediction: Prediction
    tech_stack: TechStack
    database: Database
    apis: list[ApiEndpoint]
    diagrams: Diagrams
    created_at: str
