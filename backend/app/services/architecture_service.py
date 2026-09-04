"""Rule-driven generation of tech stack, database schema, and API spec (PRD sections 22-24).

This is deliberately NOT ML -- the architecture *style* comes from ml_service; this
module maps {style, requirements} to concrete artifacts, varying by real-time,
payment, budget and scale rather than using one fixed stack for every project.
"""
import re

from app.schemas.schemas import ApiEndpoint, Database, DbTable, Prediction, Requirements, TechStack

_WORD_RE = re.compile(r"[a-z]+")


def _pascal(name: str) -> str:
    return "".join(w.capitalize() for w in _WORD_RE.findall(name.lower())) or "Entity"


def generate_tech_stack(requirements: Requirements, prediction: Prediction, budget: str) -> TechStack:
    architecture = prediction.architecture

    frontend = ["React"]
    if budget == "high":
        frontend.append("TypeScript")

    if architecture == "Serverless":
        backend = ["AWS Lambda", "API Gateway"] if budget != "low" else ["Cloud Functions"]
    elif architecture == "Microservices":
        backend = ["FastAPI", "Node.js (Express)"] if requirements.real_time else ["FastAPI"]
    else:
        backend = ["FastAPI"] if budget == "low" else ["Django"]

    database = ["PostgreSQL"]
    if requirements.data_complexity == "high" or len(requirements.modules) > 6:
        database.append("Redis")
    if "analytics" in requirements.modules or requirements.data_complexity == "high":
        database.append("MongoDB")

    messaging = []
    if architecture == "Microservices" and (requirements.real_time or len(requirements.external_integrations) >= 3):
        messaging.append("Kafka" if budget == "high" else "RabbitMQ")
    if requirements.real_time and architecture != "Serverless":
        messaging.append("WebSockets")

    infrastructure = []
    if architecture == "Monolith":
        infrastructure = ["Docker"] if budget != "low" else ["Single VM"]
    elif architecture == "Microservices":
        infrastructure = ["Docker", "Kubernetes"] if budget == "high" else ["Docker", "Docker Compose"]
    else:
        infrastructure = ["Serverless Framework", "CloudWatch"]

    if requirements.payment:
        infrastructure.append("Stripe/Razorpay SDK")

    return TechStack(
        frontend=frontend,
        backend=backend,
        database=database,
        messaging=messaging,
        infrastructure=infrastructure,
    )


def generate_database(requirements: Requirements) -> Database:
    tables = []

    for actor in requirements.actors:
        entity = _pascal(actor)
        columns = [f"{actor.lower()}_id PK", "name", "email", "created_at"]
        tables.append(DbTable(name=entity, columns=columns))

    if "ordering" in requirements.modules or "browsing" in requirements.modules:
        primary_actor = requirements.actors[0].lower() if requirements.actors else "customer"
        tables.append(DbTable(
            name="Order",
            columns=[
                "order_id PK",
                f"{primary_actor}_id FK",
                "status",
                "total",
                "created_at",
            ],
        ))

    if requirements.payment:
        tables.append(DbTable(
            name="Payment",
            columns=["payment_id PK", "order_id FK", "amount", "method", "status", "paid_at"],
        ))

    if "tracking" in requirements.modules:
        tables.append(DbTable(
            name="TrackingEvent",
            columns=["event_id PK", "order_id FK", "status", "location", "timestamp"],
        ))

    if "notifications" in requirements.modules:
        tables.append(DbTable(
            name="Notification",
            columns=["notification_id PK", "recipient_id FK", "channel", "message", "sent_at"],
        ))

    if "reviews" in requirements.modules:
        tables.append(DbTable(
            name="Review",
            columns=["review_id PK", "author_id FK", "target_id", "rating", "comment", "created_at"],
        ))

    return Database(tables=tables[:8])


def generate_apis(requirements: Requirements) -> list[ApiEndpoint]:
    apis = [
        ApiEndpoint(method="POST", path="/api/auth/register", purpose="Register a new user"),
        ApiEndpoint(method="POST", path="/api/auth/login", purpose="Authenticate a user"),
    ]

    if "browsing" in requirements.modules:
        resource = requirements.domain.split("_")[0] if requirements.domain else "items"
        apis.append(ApiEndpoint(method="GET", path=f"/api/{resource}", purpose=f"List {resource}"))

    if "ordering" in requirements.modules:
        apis.append(ApiEndpoint(method="POST", path="/api/orders", purpose="Create a new order"))
        apis.append(ApiEndpoint(method="GET", path="/api/orders/:id", purpose="Get order details"))

    if requirements.payment:
        apis.append(ApiEndpoint(method="POST", path="/api/payments", purpose="Process a payment"))

    if "tracking" in requirements.modules:
        apis.append(ApiEndpoint(method="GET", path="/api/orders/:id/track", purpose="Track order status"))

    if "notifications" in requirements.modules:
        apis.append(ApiEndpoint(method="POST", path="/api/notifications", purpose="Send a notification"))

    if "reviews" in requirements.modules:
        apis.append(ApiEndpoint(method="POST", path="/api/reviews", purpose="Submit a review"))

    for integration in requirements.external_integrations:
        apis.append(ApiEndpoint(
            method="GET",
            path=f"/api/integrations/{integration}/status",
            purpose=f"Check {integration} integration health",
        ))

    return apis[:10]
