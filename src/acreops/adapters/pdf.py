from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from acreops.config import get_settings

NAVY = colors.HexColor("#0F2744")
TEAL = colors.HexColor("#1F6F6A")
SAND = colors.HexColor("#F4EFE6")
SLATE = colors.HexColor("#334155")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=22,
            textColor=NAVY,
            spaceAfter=6,
            leading=26,
        ),
        "kicker": ParagraphStyle(
            "kicker",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=TEAL,
            tracking=1.2,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=13,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=SLATE,
            leading=13,
            alignment=TA_JUSTIFY,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=SLATE,
            leading=11,
            alignment=TA_LEFT,
        ),
    }


def _table(data: list[list[str]], col_widths: list[float] | None = None) -> Table:
    table = Table(data, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("BACKGROUND", (0, 1), (-1, -1), SAND),
                ("TEXTCOLOR", (0, 1), (-1, -1), SLATE),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D6D3C9")),
            ]
        )
    )
    return table


def write_report(filename: str, title: str, kicker: str, sections: list[tuple[str, str, list[list[str]] | None]]) -> Path:
    settings = get_settings()
    out_dir = settings.acreops_artifact_dir / "pdfs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename

    styles = _styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=title,
        author="AcreOps",
    )
    story: list = [
        Paragraph("ACREOPS  ·  REAL ESTATE & CONSTRUCTION AGENTS", styles["kicker"]),
        Paragraph(title, styles["cover"]),
        Paragraph(kicker, styles["small"]),
        Spacer(1, 10),
    ]
    for heading, body, rows in sections:
        story.append(Paragraph(heading, styles["h2"]))
        if body:
            story.append(Paragraph(body.replace("\n", "<br/>"), styles["body"]))
            story.append(Spacer(1, 6))
        if rows:
            story.append(_table(rows))
    story.append(Spacer(1, 18))
    story.append(
        Paragraph(
            "Prepared by AcreOps agents. Outputs are decision-support, not a licensed appraisal, "
            "PE stamp, or legal opinion. Validate with a qualified professional before signing.",
            styles["small"],
        )
    )
    doc.build(story)
    return path
