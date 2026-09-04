"""Assembles the final PDF report (PRD section 26)."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.schemas import Database, Diagrams, Prediction, Requirements, TechStack

REPORTS_DIR = Path(__file__).parent.parent.parent.parent / "reports"

INK = colors.HexColor("#0E2A3F")
CYANOTYPE = colors.HexColor("#3E7CB1")
AMBER = colors.HexColor("#D98E36")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontSize=20, textColor=INK, spaceAfter=4, leading=24))
    styles.add(ParagraphStyle(name="SectionHeading", fontSize=13, textColor=CYANOTYPE, spaceBefore=16, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", fontSize=10, textColor=INK, leading=14))
    return styles


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
    evaluation: dict | None = None,
) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = REPORTS_DIR / f"{report_id}.pdf"
    styles = _styles()

    doc = SimpleDocTemplate(str(out_path), pagesize=LETTER, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    story = []

    story.append(Paragraph("ARCH GEN AI — Architecture Report", styles["ReportTitle"]))
    story.append(Paragraph(f"Report ID: {report_id}", styles["Body"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Project Description", styles["SectionHeading"]))
    story.append(Paragraph(description, styles["Body"]))

    story.append(Paragraph("2. Extracted Requirements", styles["SectionHeading"]))
    story.append(Paragraph(f"Domain: {requirements.domain}", styles["Body"]))
    story.append(Paragraph(f"Actors: {', '.join(requirements.actors)}", styles["Body"]))
    story.append(Paragraph(f"Modules: {', '.join(requirements.modules)}", styles["Body"]))
    story.append(Paragraph(f"Real-time: {requirements.real_time} | Payment: {requirements.payment}", styles["Body"]))
    story.append(Paragraph(f"External integrations: {', '.join(requirements.external_integrations) or 'none'}", styles["Body"]))
    story.append(Paragraph(f"Data complexity: {requirements.data_complexity}", styles["Body"]))

    story.append(Paragraph("3. Architecture Prediction", styles["SectionHeading"]))
    story.append(Paragraph(f"Recommended architecture: <b>{prediction.architecture}</b>", styles["Body"]))
    story.append(Paragraph(f"Confidence: {round(prediction.confidence * 100)}%", styles["Body"]))
    story.append(Paragraph(f"Model: {model_version}", styles["Body"]))

    story.append(Paragraph("4. Deciding Factors", styles["SectionHeading"]))
    factor_rows = [["Factor", "Importance"]] + [
        [f.name, f"{round(f.importance * 100)}%"] for f in prediction.top_factors
    ]
    story.append(_table(factor_rows))

    story.append(Paragraph("5. Technology Stack", styles["SectionHeading"]))
    stack_rows = [["Category", "Selection"]] + [
        [category, ", ".join(items)]
        for category, items in [
            ("Frontend", tech_stack.frontend),
            ("Backend", tech_stack.backend),
            ("Database", tech_stack.database),
            ("Messaging", tech_stack.messaging),
            ("Infrastructure", tech_stack.infrastructure),
        ]
        if items
    ]
    story.append(_table(stack_rows))

    story.append(Paragraph("6. Database Schema", styles["SectionHeading"]))
    for table in database.tables:
        story.append(Paragraph(f"<b>{table.name}</b>: {', '.join(table.columns)}", styles["Body"]))

    story.append(Paragraph("7. API Specification", styles["SectionHeading"]))
    api_rows = [["Method", "Path", "Purpose"]] + [[a.method, a.path, a.purpose] for a in apis]
    story.append(_table(api_rows))

    story.append(Paragraph("8. Architecture Diagram", styles["SectionHeading"]))
    story.append(Paragraph(diagrams.architecture.caption, styles["Body"]))

    story.append(Paragraph("9. Deployment Diagram", styles["SectionHeading"]))
    story.append(Paragraph(diagrams.deployment.caption, styles["Body"]))

    story.append(Paragraph("10. ML Model Information", styles["SectionHeading"]))
    story.append(Paragraph(f"Trained classifier: {model_version}", styles["Body"]))

    if evaluation:
        story.append(Paragraph("11. Evaluation Information", styles["SectionHeading"]))
        story.append(Paragraph(
            f"Accuracy: {evaluation.get('accuracy', 0):.2%} | "
            f"Precision: {evaluation.get('precision', 0):.2%} | "
            f"Recall: {evaluation.get('recall', 0):.2%} | "
            f"F1: {evaluation.get('f1', 0):.2%}",
            styles["Body"],
        ))

    doc.build(story)
    return out_path


def _table(rows: list[list[str]]) -> Table:
    t = Table(rows, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t
