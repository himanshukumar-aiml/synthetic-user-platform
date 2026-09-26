from backend.llm import llm


def extract_insights(
    product_name: str,
    research_objective: str,
    survey_results: list[dict]
) -> str:

    responses = ""

    for result in survey_results:

        persona = result["persona"]

        responses += f"""
PERSONA: {persona.name}
AGE: {persona.age}
OCCUPATION: {persona.occupation}

RESPONSE:
{result["answer"]}

-------------------------
"""

    prompt = f"""
You are a research insight extraction agent.

PRODUCT:
{product_name}

RESEARCH OBJECTIVE:
{research_objective}

SYNTHETIC USER SURVEY RESPONSES:
{responses}

Analyze the responses and create a structured research insight report.

Include:

1. Overall Summary
2. Common Themes
3. Key Differences Between Personas
4. User Motivations
5. Pain Points and Concerns
6. Feature Preferences
7. Price and Willingness to Pay
8. Key Research Findings
9. Product Recommendations

Important:
- Base the analysis only on the provided responses.
- Do not invent information.
- Clearly distinguish common patterns from individual opinions.
- Do not treat synthetic users as statistically representative real users.
- Keep the analysis useful for product research.
"""

    response = llm.invoke(prompt)

    return response.content