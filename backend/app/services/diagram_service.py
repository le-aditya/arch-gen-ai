"""Builds structured node/edge diagrams from the generated tech stack and schema
(PRD section 25) -- dynamic per project rather than static ASCII strings."""
from app.schemas.schemas import Database, Diagram, DiagramEdge, DiagramNode, Diagrams, Prediction, TechStack


def _service_name(table_name: str) -> str:
    return f"{table_name} Service"


def build_architecture_diagram(prediction: Prediction, database: Database) -> Diagram:
    nodes = [DiagramNode(id="user", label="User", kind="client")]
    edges = []

    if prediction.architecture == "Monolith":
        nodes.append(DiagramNode(id="app", label="Application Server", kind="service"))
        nodes.append(DiagramNode(id="db", label="Database", kind="database"))
        edges.append(DiagramEdge(source="user", target="app"))
        edges.append(DiagramEdge(source="app", target="db"))
        caption = "Monolith — single application server"
    elif prediction.architecture == "Serverless":
        nodes.append(DiagramNode(id="gateway", label="API Gateway", kind="gateway"))
        nodes.append(DiagramNode(id="functions", label="Cloud Functions", kind="service"))
        nodes.append(DiagramNode(id="db", label="Managed Database", kind="database"))
        edges += [
            DiagramEdge(source="user", target="gateway"),
            DiagramEdge(source="gateway", target="functions"),
            DiagramEdge(source="functions", target="db"),
        ]
        caption = "Serverless — API Gateway triggers on-demand functions"
    else:
        nodes.append(DiagramNode(id="gateway", label="API Gateway", kind="gateway"))
        edges.append(DiagramEdge(source="user", target="gateway"))
        for table in database.tables[:4]:
            service_id = f"svc_{table.name.lower()}"
            db_id = f"db_{table.name.lower()}"
            nodes.append(DiagramNode(id=service_id, label=_service_name(table.name), kind="service"))
            nodes.append(DiagramNode(id=db_id, label=f"{table.name} DB", kind="database"))
            edges.append(DiagramEdge(source="gateway", target=service_id))
            edges.append(DiagramEdge(source=service_id, target=db_id))
        caption = "Microservices with API Gateway"

    return Diagram(caption=caption, nodes=nodes, edges=edges)


def build_deployment_diagram(prediction: Prediction, tech_stack: TechStack) -> Diagram:
    nodes = [
        DiagramNode(id="client", label="Client", kind="client"),
        DiagramNode(id="lb", label="Load Balancer", kind="gateway"),
    ]
    edges = [DiagramEdge(source="client", target="lb")]

    if prediction.architecture == "Serverless":
        nodes.append(DiagramNode(id="functions", label="Managed Functions", kind="service"))
        edges.append(DiagramEdge(source="lb", target="functions"))
        last = "functions"
    else:
        infra_label = " + ".join(tech_stack.infrastructure) if tech_stack.infrastructure else "Application Services"
        nodes.append(DiagramNode(id="app", label=infra_label, kind="service"))
        edges.append(DiagramEdge(source="lb", target="app"))
        last = "app"

    for i, db in enumerate(tech_stack.database):
        db_id = f"store_{i}"
        nodes.append(DiagramNode(id=db_id, label=db, kind="database"))
        edges.append(DiagramEdge(source=last, target=db_id))

    for i, mq in enumerate(tech_stack.messaging):
        mq_id = f"queue_{i}"
        nodes.append(DiagramNode(id=mq_id, label=mq, kind="queue"))
        edges.append(DiagramEdge(source=last, target=mq_id))

    caption = f"Client → Load Balancer → {'Managed Functions' if prediction.architecture == 'Serverless' else 'Application Services'} → Data Layer"
    return Diagram(caption=caption, nodes=nodes, edges=edges)


def generate_diagrams(prediction: Prediction, database: Database, tech_stack: TechStack) -> Diagrams:
    return Diagrams(
        architecture=build_architecture_diagram(prediction, database),
        deployment=build_deployment_diagram(prediction, tech_stack),
    )
