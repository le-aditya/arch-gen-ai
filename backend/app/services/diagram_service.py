"""Builds structured node/edge diagrams from the generated tech stack and
requirements (PRD section 25) -- dynamic per project rather than static ASCII.

Microservice names come from the extracted modules (bounded contexts), not from
the database tables, so a project is never diagrammed with nonsense services
such as "Admin Service" purely because an Admin table exists.
"""
import re

from app.schemas.schemas import (
    Database,
    Diagram,
    DiagramEdge,
    DiagramNode,
    Diagrams,
    Prediction,
    Requirements,
    TechStack,
)

# (keywords found in a module name, service label, priority). The first rule
# that matches a module wins, so ordering matters.
_SERVICE_RULES = [
    (("auth", "identity", "login", "signup"), "Identity Service", 100),
    (("payment", "billing", "checkout"), "Payment Service", 95),
    (("course", "catalog", "curriculum", "lesson"), "Course Service", 90),
    (("quiz", "assessment", "exam", "grade", "assignment", "submission"), "Assessment Service", 85),
    (("video", "media", "stream", "content"), "Media Service", 80),
    (("progress", "learning"), "Progress Service", 70),
    (("notification", "email", "sms", "alert"), "Notification Service", 65),
    (("recommend", "personaliz"), "Recommendation Service", 55),
    (("analytic", "dashboard", "insight"), "Analytics Service", 50),
    (("order", "cart", "booking", "reservation"), "Ordering Service", 90),
    (("inventory", "product", "stock"), "Inventory Service", 85),
    (("chat", "message", "comment"), "Messaging Service", 60),
    (("search",), "Search Service", 55),
    (("review", "rating", "feedback"), "Review Service", 55),
    (("track", "delivery"), "Tracking Service", 75),
]

_CACHE_NAMES = ("redis", "memcached", "elasticache")


def _service_label(module: str) -> tuple[str, int] | None:
    lowered = module.lower()
    for keywords, label, priority in _SERVICE_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label, priority
    return None


def _fallback_label(module: str) -> str:
    words = [w for w in re.split(r"[^a-zA-Z]+", module) if w]
    name = " ".join(words[:2]).title() if words else "Core"
    return f"{name} Service"


def _services(requirements: Requirements | None, limit: int = 5) -> list[str]:
    if requirements is None:
        return ["Application Service"]

    matched: list[tuple[str, int, int]] = []
    seen: set[str] = set()
    for order, module in enumerate(requirements.modules):
        rule = _service_label(module)
        if rule is None:
            continue
        label, priority = rule
        if label in seen:
            continue
        seen.add(label)
        matched.append((label, priority, order))

    if not matched:
        for order, module in enumerate(requirements.modules[:limit]):
            matched.append((_fallback_label(module), 50, order))

    if not matched:
        return ["Core Service"]

    ranked = sorted(matched, key=lambda item: (-item[1], item[2]))[:limit]
    return [label for label, _, _ in sorted(ranked, key=lambda item: item[2])]


def _database_labels(tech_stack: TechStack | None) -> tuple[str, str | None]:
    """Split the stack's data tier into a primary store and an optional cache."""
    if not tech_stack or not tech_stack.database:
        return "Primary Database", None
    primary = tech_stack.database[0]
    cache = next(
        (item for item in tech_stack.database[1:]
         if any(name in item.lower() for name in _CACHE_NAMES)),
        None,
    )
    return primary, cache


def build_architecture_diagram(
    prediction: Prediction,
    database: Database,
    tech_stack: TechStack | None = None,
    requirements: Requirements | None = None,
) -> Diagram:
    nodes = [DiagramNode(id="user", label="Client Application", kind="client")]
    edges: list[DiagramEdge] = []
    primary_db, cache = _database_labels(tech_stack)
    queues = [
        item for item in (tech_stack.messaging if tech_stack else [])
        if "websocket" not in item.lower()
    ]

    if prediction.architecture == "Monolith":
        backend = tech_stack.backend[0] if tech_stack and tech_stack.backend else "Application Server"
        nodes.append(DiagramNode(id="app", label=f"Application Server ({backend})", kind="service"))
        nodes.append(DiagramNode(id="db", label=primary_db, kind="database"))
        edges.append(DiagramEdge(source="user", target="app"))
        edges.append(DiagramEdge(source="app", target="db"))
        if cache:
            nodes.append(DiagramNode(id="cache", label=f"{cache} (cache)", kind="database"))
            edges.append(DiagramEdge(source="app", target="cache"))
        caption = "Monolith — a single deployable application server in front of one primary database"

    elif prediction.architecture == "Serverless":
        nodes.append(DiagramNode(id="gateway", label="API Gateway", kind="gateway"))
        nodes.append(DiagramNode(id="functions", label="Cloud Functions", kind="service"))
        nodes.append(DiagramNode(id="db", label=f"Managed {primary_db}", kind="database"))
        edges += [
            DiagramEdge(source="user", target="gateway"),
            DiagramEdge(source="gateway", target="functions"),
            DiagramEdge(source="functions", target="db"),
        ]
        if queues:
            nodes.append(DiagramNode(id="queue", label=queues[0], kind="queue"))
            edges.append(DiagramEdge(source="functions", target="queue"))
        caption = "Serverless — API Gateway invokes on-demand functions over a managed data store"

    else:
        nodes.append(DiagramNode(id="gateway", label="API Gateway", kind="gateway"))
        edges.append(DiagramEdge(source="user", target="gateway"))

        services = _services(requirements)
        nodes.append(DiagramNode(id="db", label=primary_db, kind="database"))
        if cache:
            nodes.append(DiagramNode(id="cache", label=f"{cache} (cache)", kind="database"))
        if queues:
            nodes.append(DiagramNode(id="queue", label=queues[0], kind="queue"))

        for index, label in enumerate(services):
            service_id = f"svc_{index}"
            nodes.append(DiagramNode(id=service_id, label=label, kind="service"))
            edges.append(DiagramEdge(source="gateway", target=service_id))
            edges.append(DiagramEdge(source=service_id, target="db"))
            if cache:
                edges.append(DiagramEdge(source=service_id, target="cache"))
            if queues:
                edges.append(DiagramEdge(source=service_id, target="queue"))

        caption = (
            f"Microservices — {len(services)} independently deployable services "
            "behind an API gateway, sharing the primary data tier"
        )

    return Diagram(caption=caption, nodes=nodes, edges=edges)


def _app_tier_label(prediction: Prediction, tech_stack: TechStack) -> str:
    infra = tech_stack.infrastructure or []
    runtime = next((item for item in tech_stack.backend if item), "Application")
    if prediction.architecture == "Serverless":
        return "Managed Functions"
    if any("kubernetes" in item.lower() for item in infra):
        return "Kubernetes Cluster"
    if any("docker compose" in item.lower() for item in infra):
        return "Docker Compose Host"
    if any("docker" in item.lower() for item in infra):
        return "Docker Host"
    if any("vm" in item.lower() for item in infra):
        return "Application VM"
    return f"{runtime} Runtime"


def build_deployment_diagram(prediction: Prediction, tech_stack: TechStack) -> Diagram:
    # Serverless has no load balancer to operate: the API gateway is the entry point.
    entry_label = "API Gateway" if prediction.architecture == "Serverless" else "Load Balancer"
    nodes = [
        DiagramNode(id="client", label="Web / Mobile Client", kind="client"),
        DiagramNode(id="lb", label=entry_label, kind="gateway"),
    ]
    edges = [DiagramEdge(source="client", target="lb")]

    app_label = _app_tier_label(prediction, tech_stack)
    nodes.append(DiagramNode(id="app", label=app_label, kind="service"))
    edges.append(DiagramEdge(source="lb", target="app"))
    last = "app"

    primary_db, cache = _database_labels(tech_stack)
    nodes.append(DiagramNode(id="store_primary", label=primary_db, kind="database"))
    edges.append(DiagramEdge(source=last, target="store_primary"))

    if cache:
        nodes.append(DiagramNode(id="store_cache", label=f"{cache} (cache)", kind="database"))
        edges.append(DiagramEdge(source=last, target="store_cache"))

    queues = [
        item for item in tech_stack.messaging
        if "websocket" not in item.lower()
    ]
    if queues:
        nodes.append(DiagramNode(id="queue_0", label=queues[0], kind="queue"))
        edges.append(DiagramEdge(source=last, target="queue_0"))

    data_tier = primary_db + (" + " + cache if cache else "")
    caption = f"Client → {entry_label} → {app_label} → {data_tier}"
    return Diagram(caption=caption, nodes=nodes, edges=edges)


def generate_diagrams(
    prediction: Prediction,
    database: Database,
    tech_stack: TechStack,
    requirements: Requirements | None = None,
) -> Diagrams:
    return Diagrams(
        architecture=build_architecture_diagram(prediction, database, tech_stack, requirements),
        deployment=build_deployment_diagram(prediction, tech_stack),
    )
