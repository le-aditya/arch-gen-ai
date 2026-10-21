"""Rule-driven generation of tech stack, database schema, and API spec (PRD sections 22-24).

This is deliberately NOT ML -- the architecture *style* comes from ml_service; this
module maps {style, requirements} to concrete artifacts, varying by real-time,
payment, budget and scale rather than using one fixed stack for every project.

Schema and API generation are driven by the extracted modules, so an online
learning platform gets Course/Lesson/Enrollment tables and course endpoints
instead of a generic Order table. Foreign keys are only emitted when the
referenced table actually exists in the generated schema.
"""
import re

from app.schemas.schemas import ApiEndpoint, Database, DbTable, Prediction, Requirements, TechStack

_WORD_RE = re.compile(r"[a-z]+")

MAX_TABLES = 14
MAX_ENDPOINTS = 16

# Higher priority wins a slot when there are more candidate tables than the cap.
_PRIORITY = {
    "Course": 96,
    "Enrollment": 94,
    "Payment": 92,
    "Quiz": 88,
    "Assignment": 87,
    "Question": 86,
    "Submission": 85,
    "Booking": 85,
    "Order": 85,
    "Progress": 80,
    "Notification": 78,
    "Lesson": 74,
    "TrackingEvent": 74,
    "Review": 70,
    "Message": 68,
    "Product": 66,
    "OrderItem": 64,
    "AnalyticsEvent": 60,
    "MediaAsset": 58,
    "Recommendation": 56,
}


def _pascal(name: str) -> str:
    return "".join(w.capitalize() for w in _WORD_RE.findall(name.lower())) or "Entity"


def _snake(name: str) -> str:
    return "_".join(_WORD_RE.findall(name.lower())) or "entity"


def _plural(name: str) -> str:
    lowered = name.lower()
    if lowered.endswith(("s", "x", "z", "ch", "sh")):
        return lowered + "es"
    if lowered.endswith("y") and lowered[-2:-1] not in "aeiou":
        return lowered[:-1] + "ies"
    return lowered + "s"


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
    if architecture == "Microservices" and (
        requirements.real_time or len(requirements.external_integrations) >= 3
    ):
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


def _table(name: str, columns: list[tuple[str, str | None]], order: int) -> dict:
    return {
        "name": name,
        "columns": columns,
        "priority": _PRIORITY.get(name, 50),
        "order": order,
    }


def _module_tables(
    module: str,
    actor_entities: list[str],
    primary_entity: str | None,
    order: int,
) -> list[dict]:
    """Map one extracted module name to the tables it implies."""

    def actor_ref(preferred: str) -> str | None:
        if not actor_entities:
            return None
        for entity in actor_entities:
            if preferred in entity.lower():
                return entity
        return primary_entity

    def actor_column(preferred: str = "") -> tuple[str, str | None]:
        entity = actor_ref(preferred) if preferred else primary_entity
        if entity is None:
            return ("user_id", None)
        return (f"{_snake(entity)}_id", entity)

    lowered = module.lower()
    tables: list[dict] = []

    if any(key in lowered for key in ("course", "catalog", "curriculum", "lesson", "class", "enroll")):
        tables.append(_table("Course", [
            ("course_id", "PK"),
            ("instructor_id", actor_ref("instructor")),
            ("title", None),
            ("description", None),
            ("price", None),
            ("status", None),
            ("created_at", None),
        ], order))
        tables.append(_table("Lesson", [
            ("lesson_id", "PK"),
            ("course_id", "Course"),
            ("title", None),
            ("content_url", None),
            ("duration_min", None),
            ("position", None),
        ], order))
        tables.append(_table("Enrollment", [
            ("enrollment_id", "PK"),
            ("course_id", "Course"),
            actor_column(),
            ("status", None),
            ("enrolled_at", None),
        ], order))

    if any(key in lowered for key in ("video", "media", "stream")):
        tables.append(_table("MediaAsset", [
            ("asset_id", "PK"),
            ("lesson_id", "Lesson"),
            ("provider", None),
            ("playback_url", None),
            ("encoding_status", None),
            ("created_at", None),
        ], order))

    if any(key in lowered for key in ("quiz", "assessment", "exam")):
        tables.append(_table("Quiz", [
            ("quiz_id", "PK"),
            ("course_id", "Course"),
            ("title", None),
            ("total_marks", None),
            ("duration_min", None),
            ("published_at", None),
        ], order))
        tables.append(_table("Question", [
            ("question_id", "PK"),
            ("quiz_id", "Quiz"),
            ("prompt", None),
            ("kind", None),
            ("marks", None),
        ], order))
        tables.append(_table("QuizAttempt", [
            ("attempt_id", "PK"),
            ("quiz_id", "Quiz"),
            actor_column(),
            ("score", None),
            ("submitted_at", None),
        ], order))

    if any(key in lowered for key in ("assignment", "submission", "grading")):
        tables.append(_table("Assignment", [
            ("assignment_id", "PK"),
            ("course_id", "Course"),
            ("title", None),
            ("instructions", None),
            ("due_at", None),
            ("max_score", None),
        ], order))
        tables.append(_table("Submission", [
            ("submission_id", "PK"),
            ("assignment_id", "Assignment"),
            actor_column(),
            ("file_url", None),
            ("score", None),
            ("submitted_at", None),
        ], order))

    if any(key in lowered for key in ("progress", "track")):
        if "track" in lowered and "progress" not in lowered:
            tables.append(_table("TrackingEvent", [
                ("event_id", "PK"),
                ("order_id", "Order"),
                ("status", None),
                ("location", None),
                ("occurred_at", None),
            ], order))
        else:
            tables.append(_table("Progress", [
                ("progress_id", "PK"),
                actor_column(),
                ("lesson_id", "Lesson"),
                ("percent_complete", None),
                ("updated_at", None),
            ], order))

    if any(key in lowered for key in ("payment", "billing", "checkout")):
        tables.append(_table("Payment", [
            ("payment_id", "PK"),
            ("enrollment_id", "Enrollment"),
            actor_column(),
            ("amount", None),
            ("currency", None),
            ("method", None),
            ("status", None),
            ("paid_at", None),
        ], order))

    if any(key in lowered for key in ("notification", "email", "sms", "alert")):
        tables.append(_table("Notification", [
            ("notification_id", "PK"),
            actor_column(),
            ("channel", None),
            ("subject", None),
            ("message", None),
            ("sent_at", None),
        ], order))

    if any(key in lowered for key in ("recommend", "personaliz")):
        tables.append(_table("Recommendation", [
            ("recommendation_id", "PK"),
            actor_column(),
            ("course_id", "Course"),
            ("score", None),
            ("reason", None),
            ("generated_at", None),
        ], order))

    if any(key in lowered for key in ("analytic", "dashboard", "report", "insight")):
        tables.append(_table("AnalyticsEvent", [
            ("event_id", "PK"),
            actor_column(),
            ("event_type", None),
            ("payload", None),
            ("occurred_at", None),
        ], order))

    if any(key in lowered for key in ("order", "cart", "checkout")):
        tables.append(_table("Order", [
            ("order_id", "PK"),
            actor_column(),
            ("status", None),
            ("total", None),
            ("created_at", None),
        ], order))
        tables.append(_table("OrderItem", [
            ("item_id", "PK"),
            ("order_id", "Order"),
            ("product_id", "Product"),
            ("quantity", None),
            ("unit_price", None),
        ], order))

    if any(key in lowered for key in ("inventory", "product", "stock")):
        tables.append(_table("Product", [
            ("product_id", "PK"),
            ("name", None),
            ("description", None),
            ("price", None),
            ("stock", None),
        ], order))

    if any(key in lowered for key in ("booking", "reservation", "appointment")):
        tables.append(_table("Booking", [
            ("booking_id", "PK"),
            actor_column(),
            ("resource_id", None),
            ("starts_at", None),
            ("ends_at", None),
            ("status", None),
        ], order))

    if any(key in lowered for key in ("chat", "message", "comment")):
        tables.append(_table("Message", [
            ("message_id", "PK"),
            actor_column(),
            ("recipient_id", None),
            ("body", None),
            ("sent_at", None),
        ], order))

    if any(key in lowered for key in ("review", "rating", "feedback")):
        tables.append(_table("Review", [
            ("review_id", "PK"),
            actor_column(),
            ("target_id", None),
            ("rating", None),
            ("comment", None),
            ("created_at", None),
        ], order))

    return tables


def generate_database(requirements: Requirements) -> Database:
    actor_entities: list[str] = []
    for actor in requirements.actors:
        entity = _pascal(actor)
        if entity not in actor_entities:
            actor_entities.append(entity)

    primary_entity = actor_entities[0] if actor_entities else None

    candidates: list[dict] = []
    seen: set[str] = set()
    for order, module in enumerate(requirements.modules):
        for table in _module_tables(module, actor_entities, primary_entity, order):
            if table["name"] in seen:
                continue
            seen.add(table["name"])
            candidates.append(table)

    # Flags can be true even when the LLM did not name a matching module.
    for name in ("Payment", "Notification"):
        flagged = name == "Payment" and requirements.payment
        flagged = flagged or (name == "Notification" and "notifications" in requirements.modules)
        if flagged and name not in seen:
            seen.add(name)
            generated = _module_tables(name.lower(), actor_entities, primary_entity, len(candidates))
            candidates.extend(generated)

    actor_tables = [
        {
            "name": entity,
            "columns": [
                (f"{_snake(entity)}_id", "PK"),
                ("name", None),
                ("email", None),
                ("created_at", None),
            ],
            "priority": 100,
            "order": -1,
        }
        for entity in actor_entities
    ]

    slots = MAX_TABLES - len(actor_tables)
    business = sorted(candidates, key=lambda t: (-t["priority"], t["order"]))[:max(0, slots)]
    business.sort(key=lambda t: t["order"])

    selected = actor_tables + business
    selected_names = {table["name"] for table in selected}

    tables: list[DbTable] = []
    for table in selected:
        columns = []
        for column, reference in table["columns"]:
            if reference == "PK":
                columns.append(f"{column} PK")
            elif reference and reference in selected_names:
                columns.append(f"{column} FK")
            else:
                columns.append(column)
        tables.append(DbTable(name=table["name"], columns=columns))

    return Database(tables=tables[:MAX_TABLES])


_ENTITY_ACTIONS = {
    "Course": ("List all courses", "Create a new course", "Fetch a course with its lessons"),
    "Enrollment": ("List enrollments", "Enroll a student in a course", "Fetch an enrollment"),
    "Payment": ("List payments", "Initiate a payment", "Fetch a payment receipt"),
    "Quiz": ("List quizzes for a course", "Create a quiz", "Fetch a quiz with its questions"),
    "Assignment": ("List assignments", "Create an assignment", "Fetch an assignment"),
    "Submission": ("List submissions", "Submit an assignment", "Fetch a submission"),
    "Progress": ("Get a learner's progress", "Record a progress update", "Fetch progress detail"),
    "Notification": ("List notifications", "Send a notification", "Fetch a notification"),
    "Order": ("List orders", "Create a new order", "Fetch order details"),
    "Booking": ("List bookings", "Create a booking", "Fetch booking details"),
    "Product": ("List products", "Create a product", "Fetch product details"),
    "Review": ("List reviews", "Submit a review", "Fetch review details"),
}


def generate_apis(requirements: Requirements) -> list[ApiEndpoint]:
    apis: list[ApiEndpoint] = [
        ApiEndpoint(method="POST", path="/api/auth/register", purpose="Register a new user"),
        ApiEndpoint(method="POST", path="/api/auth/login", purpose="Authenticate a user"),
    ]

    database = generate_database(requirements)
    actor_names = {_pascal(actor) for actor in requirements.actors}
    business = [table for table in database.tables if table.name not in actor_names]
    business.sort(key=lambda table: -_PRIORITY.get(table.name, 50))

    for table in business[:3]:
        resource = _plural(table.name)
        actions = _ENTITY_ACTIONS.get(
            table.name,
            (
                f"List {resource}",
                f"Create a new {table.name.lower()}",
                f"Fetch a single {table.name.lower()}",
            ),
        )
        apis.extend([
            ApiEndpoint(method="GET", path=f"/api/{resource}", purpose=actions[0]),
            ApiEndpoint(method="POST", path=f"/api/{resource}", purpose=actions[1]),
            ApiEndpoint(method="GET", path=f"/api/{resource}/:id", purpose=actions[2]),
        ])

    if requirements.payment and "payments" not in {a.path.rstrip("/").split("/")[-1] for a in apis}:
        apis.append(ApiEndpoint(method="POST", path="/api/payments", purpose="Initiate a payment"))

    if "tracking" in requirements.modules:
        apis.append(ApiEndpoint(
            method="GET", path="/api/progress/:id", purpose="Track progress for a learner"))

    for integration in requirements.external_integrations:
        if len(apis) >= MAX_ENDPOINTS:
            break
        apis.append(ApiEndpoint(
            method="GET",
            path=f"/api/integrations/{_snake(integration)}/status",
            purpose=f"Check {integration.replace('_', ' ')} integration health",
        ))

    seen: set[tuple[str, str]] = set()
    unique = []
    for endpoint in apis:
        key = (endpoint.method, endpoint.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(endpoint)

    return unique[:MAX_ENDPOINTS]
