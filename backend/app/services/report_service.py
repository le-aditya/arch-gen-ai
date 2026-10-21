"""Assembles the final PDF report (PRD section 26).

The report is the artifact users keep, so it has to carry every product of the
pipeline: the requirements extract, the classifier's decision with its per-class
probabilities and weighted deciding factors, the technology stack, the
architecture and deployment diagrams (drawn as vector figures rather than
captions alone), the relational schema, the API surface and the model's
evaluation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.schemas import (
    Database,
    Diagrams,
    FeatureVector,
    Prediction,
    Requirements,
    TechStack,
)
from app.services.pdf_diagram import diagram_flowable

REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports"
ML_METRICS_PATH = Path(__file__).parent.parent.parent / "ml" / "model_metrics.json"

INK = colors.HexColor("#0E2A3F")
CYANOTYPE = colors.HexColor("#3E7CB1")
AMBER = colors.HexColor("#D98E36")
MUTED = colors.HexColor("#6B7C8C")
RULE = colors.HexColor("#DCE3E9")
SURFACE = colors.HexColor("#F5F8FA")
HEAD_BG = colors.HexColor("#EDF2F6")

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN = 0.85 * inch
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

ARCHITECTURE_NOTES = {
    "Monolith": (
        "One deployable application containing the domain logic, served behind a "
        "single database. Fewest moving parts, cheapest to operate, and the "
        "quickest route to a working release for a small team."
    ),
    "Microservices": (
        "The domain is split into independently deployable services behind an API "
        "gateway, each owning its data. Buys independent scaling and team autonomy "
        "at the cost of distributed tracing, network failure handling and more "
        "operational work."
    ),
    "Serverless": (
        "Stateless functions invoked per request behind a managed API gateway, "
        "with a managed data store. Scales to zero and removes server operations, "
        "in exchange for cold starts, execution limits and vendor coupling."
    ),
}

FACTOR_VALUES = {
    "Team size": lambda f: f"{f.team_size} people",
    "Budget": lambda f: f.budget.capitalize(),
    "Expected user scale": lambda f: f.expected_users.capitalize(),
    "Number of actor roles": lambda f: f"{f.number_of_roles} roles",
    "Number of modules": lambda f: f"{f.number_of_modules} modules",
    "Real-time requirement": lambda f: "Yes" if f.real_time else "No",
    "Payment processing": lambda f: "Yes" if f.payment else "No",
    "External integrations": lambda f: f"{f.external_integrations} services",
    "Data complexity": lambda f: f.data_complexity.capitalize(),
    "Availability requirement": lambda f: f.availability.capitalize(),
    "Application domain": lambda f: f.domain.replace("_", " ").title(),
}

FACTOR_NOTES = {
    "Team size": "A small team carries less operational overhead, which favours a single deployable; larger teams can staff service boundaries.",
    "Budget": "Budget caps managed infrastructure, orchestration and the on-call effort you can sustain.",
    "Expected user scale": "Projected traffic drives horizontal scaling, caching and load-balancing needs.",
    "Number of actor roles": "More distinct roles mean more access-control surfaces and more bounded contexts to separate.",
    "Number of modules": "Functional breadth pushes decomposition; too much scope in one deployable slows delivery.",
    "Real-time requirement": "Live updates need persistent connections or event streaming instead of plain request/response.",
    "Payment processing": "Money movement adds compliance boundaries, webhooks and idempotency requirements.",
    "External integrations": "Each third party is a new failure domain that needs isolation and retry handling.",
    "Data complexity": "Rich or high-volume data models push toward polyglot persistence and read/write separation.",
    "Availability requirement": "Higher uptime targets justify redundancy, health checks and zero-downtime deploys.",
    "Application domain": "The domain prior reflects how comparable systems are usually built in practice.",
}

STACK_ROLES = {
    "Frontend": "User-facing screens and dashboards",
    "Backend": "Domain logic and the HTTP API surface",
    "Database": "Primary persistence and caching",
    "Messaging": "Asynchronous, decoupled processing",
    "Infrastructure": "Build, deployment and operations",
    "Integrations": "Third-party provider SDKs called by the backend",
}


def _styles() -> dict:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", fontName="Helvetica-Bold", fontSize=30, leading=34,
        textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(
        name="Eyebrow", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=AMBER, spaceAfter=10))
    styles.add(ParagraphStyle(
        name="CoverLede", fontName="Helvetica", fontSize=11, leading=16,
        textColor=MUTED, spaceAfter=18))
    styles.add(ParagraphStyle(
        name="SectionHeading", fontName="Helvetica-Bold", fontSize=12.5, leading=15,
        textColor=INK, spaceBefore=2, spaceAfter=6))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=9.6, leading=14,
        textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(
        name="Small", fontName="Helvetica", fontSize=8.2, leading=11.5,
        textColor=MUTED, spaceAfter=4))
    styles.add(ParagraphStyle(
        name="Caption", fontName="Helvetica-Oblique", fontSize=8.2, leading=11.5,
        textColor=MUTED, spaceBefore=6))
    styles.add(ParagraphStyle(
        name="TableCell", fontName="Helvetica", fontSize=8.4, leading=11,
        textColor=INK))
    styles.add(ParagraphStyle(
        name="TableHead", fontName="Helvetica-Bold", fontSize=8.4, leading=11,
        textColor=colors.white))
    styles.add(ParagraphStyle(
        name="CalloutTitle", fontName="Helvetica-Bold", fontSize=19, leading=22,
        textColor=INK))
    styles.add(ParagraphStyle(
        name="ReportBullet", fontName="Helvetica", fontSize=9.2, leading=13.5,
        textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=3))
    return styles


_SMALL_WORDS = {"and", "or", "of", "for", "to", "the", "in", "on"}


def _humanize(value: str) -> str:
    """Turn an extracted snake_case identifier into readable prose."""
    words = value.replace("_", " ").split()
    if not words:
        return value

    # "e_learning" should read as "E-Learning", not "E Learning".
    prefix = ""
    if len(words) > 1 and len(words[0]) == 1 and words[0].isalpha():
        prefix = f"{words[0].upper()}-"
        words = words[1:]
        words[0] = words[0].lower()

    readable = [
        word if index and word.lower() in _SMALL_WORDS else word[:1].upper() + word[1:]
        for index, word in enumerate(words)
    ]
    return prefix + " ".join(readable)


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    """Escape user/LLM supplied text before it enters the PDF markup."""
    safe = escape(str(text)).replace("\n", "<br/>")
    return Paragraph(safe, style)


def _bullets(items: list[str], style) -> list[Paragraph]:
    # An en dash is used as the bullet marker: unlike U+2022 it exists in the
    # WinAnsi encoding used by the built-in Helvetica, so it never renders as a
    # missing-glyph box.
    return [Paragraph(escape(item), style, bulletText="\u2013") for item in items]


def _section(number: str, title: str) -> list:
    return [
        Paragraph(
            f'<font color="#D98E36">{number}</font>&nbsp;&nbsp;{escape(title)}',
            _STYLES["SectionHeading"],
        ),
        HRFlowable(width="100%", thickness=0.8, color=RULE, spaceBefore=0, spaceAfter=10),
    ]


def _head_row(labels: list[str]) -> list:
    return [Paragraph(label, _STYLES["TableHead"]) for label in labels]


def _table(rows: list[list], col_widths: list[float], zebra: bool = True,
           align_method: bool = False) -> Table:
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if zebra:
        for index in range(1, len(rows)):
            if index % 2 == 0:
                style.append(("BACKGROUND", (0, index), (-1, index), SURFACE))
    if align_method:
        for index, row in enumerate(rows[1:], start=1):
            method = str(row[0])
            color = AMBER if method in {"POST", "PUT", "PATCH"} else CYANOTYPE
            if method == "DELETE":
                color = colors.HexColor("#B4544A")
            style.append(("TEXTCOLOR", (0, index), (0, index), color))

    # Repeat the header row when a long table spills onto the next page.
    table = Table(rows, colWidths=col_widths, hAlign="LEFT",
                  repeatRows=1 if len(rows) > 2 else 0)
    table.setStyle(TableStyle(style))
    return table


def _bar(value: float, width: float, color=CYANOTYPE) -> Table:
    value = min(max(value, 0.0), 1.0)
    filled = max(1.0, round(width * value, 2))
    empty = max(1.0, round(width - filled, 2))
    bar = Table([["", ""]], colWidths=[filled, empty], rowHeights=[5.5])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BACKGROUND", (1, 0), (1, 0), HEAD_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -1), 0, colors.white),
    ]))
    return bar


def _schema_cell(columns: list[str]) -> Paragraph:
    text = escape(", ".join(columns))
    text = text.replace(" PK", " <b>PK</b>").replace(" FK", " <b>FK</b>")
    return Paragraph(text, _STYLES["TableCell"])


def _load_metrics() -> dict:
    try:
        return json.loads(ML_METRICS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _fmt_date(value: datetime) -> str:
    return value.strftime("%d %B %Y, %H:%M UTC")


class _ReportCanvas(pdfcanvas.Canvas):
    """Adds the running header and 'Page X of Y' footer to every page."""

    def __init__(self, *args, report_id: str = "", generated: str = "", **kwargs):
        self._report_id = report_id
        self._generated = generated
        self._states: list[dict] = []
        super().__init__(*args, **kwargs)

    def showPage(self):  # noqa: N802 - reportlab API
        self._states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._states)
        for state in self._states:
            self.__dict__.update(state)
            self._decorate(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _decorate(self, total: int):
        page = self._pageNumber
        self.saveState()
        self.setStrokeColor(RULE)
        self.setLineWidth(0.6)

        if page > 1:
            self.line(MARGIN, PAGE_HEIGHT - 46, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 46)
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(CYANOTYPE)
            self.drawString(MARGIN, PAGE_HEIGHT - 40, "ARCH GEN AI")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(MUTED)
            self.drawRightString(
                PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 40,
                f"Architecture Report  ·  {self._report_id}")

        self.line(MARGIN, 46, PAGE_WIDTH - MARGIN, 46)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MUTED)
        self.drawString(MARGIN, 33, f"Generated {self._generated}")
        self.drawCentredString(PAGE_WIDTH / 2, 33, "Confidential — prepared for project planning")
        self.drawRightString(PAGE_WIDTH - MARGIN, 33, f"Page {page} of {total}")
        self.restoreState()


_STYLES: dict = {}


def generate_pdf(
    report_id: str,
    description: str,
    requirements: Requirements,
    prediction: Prediction,
    tech_stack: TechStack,
    database: Database,
    apis: list,
    diagrams: Diagrams,
    model_version: str,
    features: FeatureVector | None = None,
    budget: str = "medium",
    created_at: datetime | None = None,
) -> Path:
    global _STYLES
    _STYLES = _styles()

    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = REPORTS_DIR / f"{report_id}.pdf"
    generated_at = created_at or datetime.now(timezone.utc)
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    generated_label = _fmt_date(generated_at)

    doc = SimpleDocTemplate(
        str(out_path), pagesize=LETTER,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        leftMargin=MARGIN, rightMargin=MARGIN,
        title=f"Architecture Report {report_id}",
        author="ARCH GEN AI",
        subject=f"Recommended architecture: {prediction.architecture}",
        creator="ARCH GEN AI",
    )

    story: list = []
    body = _STYLES["Body"]
    small = _STYLES["Small"]
    cell = _STYLES["TableCell"]
    confidence = round(prediction.confidence * 100)

    # ---------------------------------------------------------------- cover
    story.append(HRFlowable(width="100%", thickness=3, color=AMBER, spaceAfter=16))
    story.append(Paragraph("Architecture assessment", _STYLES["Eyebrow"]))
    story.append(Paragraph("Architecture Report", _STYLES["ReportTitle"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"{_humanize(requirements.domain)} · {len(requirements.modules)} modules · "
        f"{len(requirements.actors)} actor roles",
        _STYLES["CoverLede"],
    ))

    meta_rows = [
        ["Report ID", report_id],
        ["Generated", generated_label],
        ["Recommended architecture", prediction.architecture],
        ["Model confidence", f"{confidence}%"],
        ["Classifier", model_version],
    ]
    meta = Table(
        [[Paragraph(f"<b>{escape(key)}</b>", cell), Paragraph(escape(value), cell)]
         for key, value in meta_rows],
        colWidths=[150, CONTENT_WIDTH - 150], hAlign="LEFT",
    )
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), SURFACE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta)
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "This report is generated from the project description below. It records the "
        "requirements extracted from that text, the architecture style selected by the "
        "trained classifier, the factors that drove that decision, and the concrete "
        "stack, schema, API surface and diagrams implied by it.",
        small,
    ))
    story.append(PageBreak())

    # ------------------------------------------------- 1. project description
    story += _section("01", "Project Description")
    story.append(_p(description, body))
    if features is not None:
        story.append(Spacer(1, 4))
        inputs = Table(
            [[
                Paragraph(f"<b>{label}</b><br/>{escape(value)}", cell)
                for label, value in [
                    ("Team size", f"{features.team_size} people"),
                    ("Budget", features.budget.capitalize()),
                    ("Expected users", features.expected_users.capitalize()),
                    ("Availability", features.availability.capitalize()),
                ]
            ]],
            colWidths=[CONTENT_WIDTH / 4] * 4,
            hAlign="LEFT",
        )
        inputs.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
            ("GRID", (0, 0), (-1, -1), 0.4, RULE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(inputs)
        story.append(Paragraph("Assessment inputs supplied with the project description.", small))

    # ------------------------------------------------------ 2. requirements
    story += _section("02", "Extracted Requirements")
    story.append(Paragraph(
        "The classifier does not read the description directly. These structured "
        "requirements are extracted from it first and then converted into the feature "
        "vector used for prediction.",
        _STYLES["Small"],
    ))
    story.append(Spacer(1, 6))
    requirement_rows = [
        _head_row(["Attribute", "Extracted value"]),
        [Paragraph("Domain", cell), Paragraph(escape(_humanize(requirements.domain)), cell)],
        [Paragraph("Actors", cell),
         Paragraph(escape(", ".join(_humanize(actor) for actor in requirements.actors) or "None"), cell)],
        [Paragraph("Modules", cell),
         Paragraph(escape(", ".join(_humanize(module) for module in requirements.modules) or "None"), cell)],
        [Paragraph("Real-time", cell), Paragraph("Yes" if requirements.real_time else "No", cell)],
        [Paragraph("Payments", cell), Paragraph("Yes" if requirements.payment else "No", cell)],
        [Paragraph("External integrations", cell),
         Paragraph(escape(", ".join(_humanize(item) for item in requirements.external_integrations) or "None"), cell)],
        [Paragraph("Data complexity", cell),
         Paragraph(requirements.data_complexity.capitalize(), cell)],
    ]
    story.append(_table(requirement_rows, [130, CONTENT_WIDTH - 130]))

    # ------------------------------------------------------- 3. recommendation
    story.append(Spacer(1, 18))
    story += _section("03", "Architecture Recommendation")
    callout = Table(
        [
            [Paragraph(escape(prediction.architecture), _STYLES["CalloutTitle"]),
             Paragraph(f"<b>{confidence}%</b><br/>model confidence",
                       ParagraphStyle("conf", parent=cell, alignment=2, fontSize=12, leading=14))],
            [Paragraph(escape(ARCHITECTURE_NOTES.get(
                prediction.architecture, "")), cell), ""],
        ],
        colWidths=[CONTENT_WIDTH - 120, 120],
        hAlign="LEFT",
    )
    callout.setStyle(TableStyle([
        ("SPAN", (1, 0), (1, 1)),
        ("SPAN", (0, 1), (0, 1)),
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, AMBER),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("VALIGN", (0, 1), (-1, 1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(callout)
    story.append(Spacer(1, 12))

    probability_rows = [_head_row(["Architecture", "Probability", "Share"])]
    for candidate in prediction.alternatives or []:
        probability_rows.append([
            Paragraph(escape(candidate.architecture), cell),
            _bar(candidate.probability, 230),
            Paragraph(f"{candidate.probability * 100:.1f}%", cell),
        ])
    if len(probability_rows) == 1:
        probability_rows.append([
            Paragraph(escape(prediction.architecture), cell),
            _bar(prediction.confidence, 230),
            Paragraph(f"{prediction.confidence * 100:.1f}%", cell),
        ])
    story.append(KeepTogether([
        Paragraph("How the classifier scored each option", _STYLES["Body"]),
        Spacer(1, 4),
        _table(probability_rows, [140, 250, 60], zebra=False),
        Paragraph(
            ("Class probabilities come from the trained classifier and sum to 100%. A "
             "narrow gap between the top two classes means the requirements sit on a "
             "boundary and should be validated before committing.")
            if len(prediction.alternatives) > 1 else
            ("Only the winning class score was available for this report; re-run the "
             "analysis to record the full class breakdown."),
            small,
        ),
    ]))

    # -------------------------------------------------------- 4. factors
    story.append(Spacer(1, 16))
    story += _section("04", "Deciding Factors")
    story.append(Paragraph(
        "These are the inputs the classifier weighted most heavily when it chose "
        f"{escape(prediction.architecture)}. The weight is each factor's share of the "
        "model's total feature importance, so the listed factors do not add up to 100%.",
        small,
    ))
    story.append(Spacer(1, 6))

    factor_rows = [_head_row(["#", "Factor", "Project value", "Weight", "", "Why it matters"])]
    if prediction.top_factors:
        for index, factor in enumerate(prediction.top_factors, start=1):
            value = "—"
            if features is not None and factor.name in FACTOR_VALUES:
                value = FACTOR_VALUES[factor.name](features)
            factor_rows.append([
                Paragraph(str(index), cell),
                Paragraph(escape(factor.name), cell),
                Paragraph(escape(value), cell),
                Paragraph(f"{factor.importance * 100:.1f}%", cell),
                _bar(factor.importance, 34, color=AMBER),
                Paragraph(escape(FACTOR_NOTES.get(factor.name, "")), cell),
            ])
    else:
        factor_rows.append([
            Paragraph("—", cell),
            Paragraph("Not available", cell),
            Paragraph("—", cell),
            Paragraph("—", cell),
            "",
            Paragraph("The classifier did not expose feature importances.", cell),
        ])

    story.append(KeepTogether([
        _table(factor_rows, [20, 112, 66, 42, 36, CONTENT_WIDTH - 276]),
        Paragraph(
            "Project value is the input that was actually supplied for this assessment; "
            "the same classifier on different inputs would rank the factors differently.",
            small,
        ),
    ]))

    # ------------------------------------------------------ 5. technology stack
    story.append(Spacer(1, 16))
    story += _section("05", "Technology Stack")
    stack_rows = [_head_row(["Category", "Selection", "Role"])]
    # The payment SDK is an integration, not deployment infrastructure; report it
    # as its own row instead of burying it in the Infrastructure line.
    infrastructure = [i for i in tech_stack.infrastructure if "SDK" not in i]
    integrations = [i for i in tech_stack.infrastructure if "SDK" in i]
    for category, items in [
        ("Frontend", tech_stack.frontend),
        ("Backend", tech_stack.backend),
        ("Database", tech_stack.database),
        ("Messaging", tech_stack.messaging),
        ("Infrastructure", infrastructure),
        ("Integrations", integrations),
    ]:
        if not items:
            continue
        stack_rows.append([
            Paragraph(f"<b>{category}</b>", cell),
            Paragraph(escape(", ".join(items)), cell),
            Paragraph(escape(STACK_ROLES.get(category, "")), cell),
        ])
    story.append(_table(stack_rows, [96, 220, CONTENT_WIDTH - 316]))

    # ----------------------------------------------------- 6. architecture diagram
    story.append(Spacer(1, 18))
    story.append(KeepTogether([
        *_section("06", "Architecture Diagram"),
        diagram_flowable(diagrams.architecture),
        Paragraph(
            f"Figure 6.1 — {escape(diagrams.architecture.caption)}. Arrows show the "
            "direction of calls at request time.",
            _STYLES["Caption"],
        ),
    ]))

    # ------------------------------------------------------ 7. deployment diagram
    story.append(Spacer(1, 18))
    story.append(KeepTogether([
        *_section("07", "Deployment Diagram"),
        diagram_flowable(diagrams.deployment),
        Paragraph(
            f"Figure 7.1 — {escape(diagrams.deployment.caption)}. Infrastructure is "
            "shown as it would be provisioned for the recommended stack.",
            _STYLES["Caption"],
        ),
    ]))

    # ---------------------------------------------------------- 8. schema
    story.append(Spacer(1, 20))
    schema_rows = [_head_row(["Table", "Columns"])]
    for table in database.tables:
        schema_rows.append([
            Paragraph(f"<b>{escape(table.name)}</b>", cell),
            _schema_cell(table.columns),
        ])
    if len(schema_rows) == 1:
        schema_rows.append([Paragraph("—", cell), Paragraph("No tables generated.", cell)])
    story.append(KeepTogether([
        *_section("08", "Database Schema"),
        Paragraph(
            "Core relational tables derived from the actor roles and modules above. "
            "<b>PK</b> marks a primary key and <b>FK</b> a foreign key.",
            small,
        ),
        Spacer(1, 6),
        _table(schema_rows, [118, CONTENT_WIDTH - 118]),
    ]))

    # ------------------------------------------------------------ 9. APIs
    story.append(Spacer(1, 20))
    story += _section("09", "API Specification")
    story.append(Paragraph(
        "Primary REST endpoints for the generated system. Paths are relative to the "
        "API root; authentication uses a bearer token issued by the login endpoint.",
        small,
    ))
    story.append(Spacer(1, 6))
    api_rows = [_head_row(["Method", "Path", "Purpose"])]
    for endpoint in apis:
        api_rows.append([
            Paragraph(f"<b>{escape(endpoint.method)}</b>", cell),
            Paragraph(escape(endpoint.path), cell),
            Paragraph(escape(endpoint.purpose), cell),
        ])
    if len(api_rows) == 1:
        api_rows.append([Paragraph("—", cell), Paragraph("—", cell), Paragraph("No endpoints generated.", cell)])
    story.append(_table(api_rows, [50, 205, CONTENT_WIDTH - 255], align_method=True))

    # ------------------------------------------------------ 10. model info
    story.append(Spacer(1, 20))
    story += _section("10", "Model Information and Evaluation")
    story.append(Paragraph(
        f"Predictions are produced by <b>{escape(model_version)}</b>, a random-forest "
        "classifier over eleven pre-development project features (team size, budget, "
        "expected users, roles, modules, real-time, payments, integrations, data "
        "complexity, availability and domain). It is trained on a synthetic dataset "
        "and evaluated on a held-out split of that data plus a separate set of real "
        "project case studies, reported below.",
        body,
    ))

    metrics = _load_metrics()
    holdout = metrics.get("holdout") or {}
    cases = metrics.get("real_case_studies") or {}
    if holdout:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Measured performance", _STYLES["Body"]))
        metric_rows = [_head_row([
            "Metric",
            f"Holdout set (n={holdout.get('n_test', '?')})",
            f"Real case studies (n={cases.get('n', '?')})",
        ])]
        for label, key in [("Accuracy", "accuracy"), ("Precision (weighted)", "precision"),
                           ("Recall (weighted)", "recall"), ("F1 score (weighted)", "f1")]:
            metric_rows.append([
                Paragraph(label, cell),
                Paragraph(f"{holdout.get(key, 0) * 100:.1f}%", cell),
                Paragraph(f"{cases.get(key, 0) * 100:.1f}%", cell),
            ])
        story.append(_table(metric_rows, [180, (CONTENT_WIDTH - 180) / 2, (CONTENT_WIDTH - 180) / 2]))

        labels = holdout.get("labels") or []
        matrix = holdout.get("confusion_matrix") or []
        if labels and matrix:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Confusion matrix (holdout set)", _STYLES["Body"]))
            matrix_rows = [_head_row(["Actual \\ Predicted"] + list(labels))]
            for label, row in zip(labels, matrix):
                matrix_rows.append([Paragraph(f"<b>{escape(str(label))}</b>", cell)]
                                   + [Paragraph(str(value), cell) for value in row])
            story.append(_table(matrix_rows, [150, 70, 70, 70]))
            story.append(Paragraph(
                "Rows are the true label, columns the predicted one. Off-diagonal "
                "entries are misclassifications, most of which sit between the two "
                "closest architecture styles.",
                small,
            ))
    else:
        story.append(Paragraph(
            "Evaluation metrics were not available when this report was generated.",
            small,
        ))

    # ------------------------------------------------- 11. assumptions
    story.append(Spacer(1, 20))
    assumptions = [
        f"Budget was given as {budget}, availability as "
        f"{features.availability if features else 'medium'}. Both directly shape the "
        "infrastructure recommendations.",
        "Requirements are inferred from free-text description. Validate the module "
        "list with stakeholders before treating it as scope.",
        f"Traffic is assumed to match an expected user scale of "
        f"{features.expected_users if features else 'medium'}.",
        "Costs, timelines and vendor choices are not modelled; the stack is a "
        "technically appropriate baseline, not a quote.",
        "Confidence reflects the classifier's training data, not certainty about the "
        "project. Treat architectures within a few points of each other as equally viable.",
    ]
    story.append(KeepTogether([
        *_section("11", "Assumptions and Limitations"),
        *_bullets(assumptions, _STYLES["ReportBullet"]),
        Spacer(1, 10),
        Paragraph("Recommended next steps", _STYLES["Body"]),
        *_bullets([
            "Review the extracted requirements and correct any missing module.",
            "Prototype the highest-risk integration before committing to the full stack.",
            "Re-run the assessment whenever team size, budget or scale assumptions change.",
        ], _STYLES["ReportBullet"]),
    ]))

    maker = partial(
        _ReportCanvas, report_id=report_id, generated=generated_label)
    doc.build(story, canvasmaker=maker)
    return out_path
