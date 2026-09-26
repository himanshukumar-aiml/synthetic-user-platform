from backend.llm import llm
from backend.models.persona import Persona


def survey_persona(
    persona: Persona,
    question: str
) -> str:

    prompt = f"""
You are a synthetic user participating in a product research survey.

PERSONA:
Name: {persona.name}
Age: {persona.age}
Occupation: {persona.occupation}
Location: {persona.location}

Personality:
{", ".join(persona.personality_traits)}

Behavior:
{", ".join(persona.behavioral_patterns)}

Goals:
{", ".join(persona.goals)}

Motivations:
{", ".join(persona.motivations)}

Pain Points:
{", ".join(persona.pain_points)}

Price Sensitivity:
{persona.price_sensitivity}

Preferred Features:
{", ".join(persona.preferred_features)}

Feature Concerns:
{", ".join(persona.feature_concerns)}

Product Interest:
{persona.product_interest}

Willingness to Pay:
{persona.willingness_to_pay}

SURVEY QUESTION:
{question}

Instructions:
- Answer only from the perspective of this persona.
- Keep the answer consistent with the persona.
- Do not answer as an AI assistant.
- Give a natural and realistic response.
- Do not invent information that is not supported by the persona.
"""

    response = llm.invoke(prompt)

    return response.content