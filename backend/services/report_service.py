import io
import html
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)


def _safe(value) -> str:
    """Escape text before placing it inside a ReportLab Paragraph."""
    return escape(str(value if value is not None else "" )).replace("\n", "<br/>")


def _persona_value(persona, *names):
    for name in names:
        value = getattr(persona, name, None)
        if value not in (None, "", [], {}):
            if isinstance(value, (list, tuple, set)):
                return ", ".join(str(item) for item in value)
            return str(value)
    return ""


def _draw_page(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D9E2F2"))
    canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#65758B"))
    canvas.drawString(18 * mm, 10 * mm, "Synthetic User Research • AI-generated simulations")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


def create_research_report(
    product_name: str,
    research_objective: str,
    survey_results: list[dict],
    insights: str,
    product_scores: list[dict] | None = None
) -> bytes:
    """Build a structured PDF research report. Scores are optional for backward compatibility."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=21 * mm,
        title=f"Synthetic User Research Report - {product_name}",
        author="Synthetic User Research Platform",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=25, alignment=TA_CENTER,
        textColor=colors.HexColor("#193B65"), spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=9,
        leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#65758B"),
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "ReportHeading", parent=styles["Heading2"], fontSize=13,
        leading=17, textColor=colors.HexColor("#193B65"),
        spaceBefore=12, spaceAfter=7, keepWithNext=True,
    )
    subheading_style = ParagraphStyle(
        "ReportSubheading", parent=styles["Heading3"], fontSize=10,
        leading=13, textColor=colors.HexColor("#2E5B88"),
        spaceBefore=7, spaceAfter=4, keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "ReportBody", parent=styles["BodyText"], fontSize=9,
        leading=13, spaceAfter=5, splitLongWords=True,
    )
    small_style = ParagraphStyle(
        "ReportSmall", parent=body_style, fontSize=8, leading=11,
    )

    story = [
        Paragraph("Synthetic User Research Report", title_style),
        Paragraph("AI-generated personas • Simulated product research", subtitle_style),
        Paragraph("Research Overview", heading_style),
        Paragraph(f"<b>Product:</b> {_safe(product_name)}", body_style),
        Paragraph(f"<b>Research Objective:</b> {_safe(research_objective)}", body_style),
        Spacer(1, 4),
    ]

    # Persona profiles and survey response highlights.
    story.append(Paragraph("Persona Profiles & Survey Response Highlights", heading_style))
    if not survey_results:
        story.append(Paragraph("No survey responses were provided for this report.", body_style))
    else:
        for index, result in enumerate(survey_results, start=1):
            persona = result.get("persona")
            if persona is None:
                persona_name = str(result.get("persona_name", f"Persona {index}"))
                age = str(result.get("age", "Not provided"))
                occupation = str(result.get("occupation", "Not provided"))
                extra_lines = []
            else:
                persona_name = _persona_value(persona, "name") or f"Persona {index}"
                age = _persona_value(persona, "age") or "Not provided"
                occupation = _persona_value(persona, "occupation", "job") or "Not provided"
                extra_lines = []
                for label, names in [
                    ("Location", ("location",)),
                    ("Goals", ("goals", "motivations", "needs")),
                    ("Pain points", ("pain_points", "challenges", "frustrations")),
                    ("Interests", ("interests", "hobbies")),
                ]:
                    value = _persona_value(persona, *names)
                    if value:
                        extra_lines.append(f"<b>{label}:</b> {_safe(value)}")

            content = [
                Paragraph(f"{index}. {_safe(persona_name)}", subheading_style),
                Paragraph(f"<b>Age:</b> {_safe(age)} &nbsp;&nbsp; <b>Occupation:</b> {_safe(occupation)}", body_style),
            ]
            content.extend(Paragraph(line, small_style) for line in extra_lines)
            answer = result.get("answer", "No response recorded.")
            content.extend([
                Paragraph("<b>Survey response highlight</b>", small_style),
                Paragraph(_safe(answer), body_style),
                Spacer(1, 5),
            ])
            story.append(KeepTogether(content))

    # Research insight output is text; preserve headings and bullets when possible.
    story.append(Paragraph("Research Insights & Findings", heading_style))
    if not insights or not insights.strip():
        story.append(Paragraph("No research insights were provided.", body_style))
    else:
        for raw_line in insights.splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 3))
                continue
            # Treat numbered headings and markdown-style headings as section headings.
            cleaned = re.sub(r"^#{1,6}\s*", "", line)
            if re.match(r"^(\d+[.)]\s+)?[A-Z][A-Za-z &/-]{2,60}:?$", cleaned) and len(cleaned) < 75:
                story.append(Paragraph(_safe(cleaned), subheading_style))
            elif re.match(r"^[-*•]\s+", line):
                bullet_text = re.sub(r"^[-*•]\s+", "", line)
                story.append(Paragraph("• " + _safe(bullet_text), body_style))
            else:
                story.append(Paragraph(_safe(cleaned), body_style))

    # Product validation scores from the scoring agent, when available.
    story.append(Paragraph("Product Validation Scores", heading_style))
    if not product_scores:
        story.append(Paragraph(
            "Product preference scores were not included. Run the product preference evaluation "
            "in the application and generate the report again to include them.", body_style
        ))
    else:
        table_data = [["Persona", "Score / 100", "Decision", "Reasoning"]]
        for result in product_scores:
            persona = result.get("persona")
            name = _persona_value(persona, "name") if persona is not None else result.get("persona_name", "Persona")
            table_data.append([
                Paragraph(_safe(name or "Persona"), small_style),
                Paragraph(_safe(result.get("score", "—")), small_style),
                Paragraph(_safe(result.get("decision", "—")), small_style),
                Paragraph(_safe(result.get("reasoning", "—")), small_style),
            ])
        table = Table(table_data, colWidths=[34 * mm, 23 * mm, 23 * mm, 76 * mm], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#193B65")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DDE8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        valid_scores = [r.get("score") for r in product_scores if isinstance(r.get("score"), (int, float))]
        if valid_scores:
            average = sum(valid_scores) / len(valid_scores)
            story.append(Spacer(1, 7))
            story.append(Paragraph(f"<b>Average synthetic preference score:</b> {average:.1f}/100", body_style))

    story.extend([
        Spacer(1, 12),
        Paragraph("Interpretation & Limitations", heading_style),
        Paragraph(
            "These results come from AI-generated synthetic personas and simulated responses. "
            "Scores and sentiment interpretations are exploratory outputs, not evidence from real customers, "
            "and should not be treated as statistically representative or as a substitute for user research.",
            body_style,
        ),
    ])

    document.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
    buffer.seek(0)
    return buffer.getvalue()
