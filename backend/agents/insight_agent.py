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

Analyze the responses and create a structured product research insight report.

Include the following sections:

1. Overall Summary

2. Common Themes
Identify the topics, needs or concerns that appear across multiple personas.

3. Sentiment Analysis
Identify the overall sentiment toward the product or topic.
Discuss positive, negative and neutral opinions.
Mention which personas express each sentiment.

4. Agreement Patterns
Identify areas where multiple personas agree.
Also identify areas where personas disagree.

5. Behavioral Trends
Identify recurring behavioral patterns such as:
- Usage habits
- Decision-making behavior
- Feature adoption tendencies
- Price-related behavior
- Reasons for using or avoiding the product

6. Key Differences Between Personas

7. User Motivations

8. Pain Points and Concerns

9. Feature Preferences

10. Price and Willingness to Pay

11. Key Research Findings

12. Product Recommendations

Important:
- Base the analysis only on the provided responses.
- Do not invent information.
- Clearly distinguish common patterns from individual opinions.
- Do not assume that an opinion shared by one persona represents all users.
- Do not treat synthetic users as statistically representative real users.
- Identify agreement only when multiple personas actually express similar views.
- Identify disagreement when personas express clearly different views.
- Keep the analysis useful for product research.
"""

    response = llm.invoke(prompt)

    return response.content