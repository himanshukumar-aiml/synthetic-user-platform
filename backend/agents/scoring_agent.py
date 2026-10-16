from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

from backend.models.persona import Persona


class ProductScore(BaseModel):
    score: int = Field(ge=0, le=100)
    reasoning: str


scoring_llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.3
).with_structured_output(ProductScore)


def score_persona(
    persona: Persona,
    product_name: str,
    research_objective: str
) -> ProductScore:

    prompt = f"""
You are a synthetic product research evaluation agent.

Evaluate whether this synthetic persona would use the given product.

PRODUCT:
{product_name}

RESEARCH OBJECTIVE:
{research_objective}

SYNTHETIC PERSONA:
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

SCORING RULES:

Give a synthetic preference score from 0 to 100.

90-100 = Very strong willingness to use
70-89 = Likely to use
40-69 = Uncertain / Maybe
20-39 = Unlikely to use
0-19 = Very unlikely to use

The score represents this synthetic persona's simulated preference,
NOT the probability that a real customer will use the product.

Consider:
- Persona goals
- Motivations
- Pain points
- Product interest
- Preferred features
- Feature concerns
- Price sensitivity
- Willingness to pay

REASONING:
Explain clearly why this persona received the score.
Base the reasoning only on the persona information provided.

Do not invent information.
"""

    return scoring_llm.invoke(prompt)