import io
import html

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


def create_research_report(
    product_name: str,
    research_objective: str,
    survey_results: list[dict],
    insights: str
) -> bytes:

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    story.append(
        Paragraph(
            "Synthetic User Research Report",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"<b>Product:</b> {html.escape(product_name)}",
            body_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<b>Research Objective:</b>",
            heading_style
        )
    )

    story.append(
        Paragraph(
            html.escape(research_objective),
            body_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Survey Responses",
            heading_style
        )
    )

    for result in survey_results:

        persona = result["persona"]

        story.append(
            Paragraph(
                f"<b>{html.escape(persona.name)}</b> "
                f"({persona.age}, {html.escape(persona.occupation)})",
                body_style
            )
        )

        story.append(
            Paragraph(
                html.escape(result["answer"]),
                body_style
            )
        )

        story.append(Spacer(1, 10))

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Research Insights",
            heading_style
        )
    )

    for line in insights.split("\n"):

        line = line.strip()

        if line:

            story.append(
                Paragraph(
                    html.escape(line),
                    body_style
                )
            )

            story.append(Spacer(1, 5))

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> Synthetic personas are "
            "AI-generated simulations and should not be treated "
            "as statistically representative real users.",
            body_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()