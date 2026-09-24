from backend.llm import llm
from backend.models.persona import ProductContext, PersonaList


persona_llm = llm.with_structured_output(PersonaList)


def generate_personas(product: ProductContext) -> PersonaList:

    prompt = f"""
You are a synthetic user persona generation agent.

Generate exactly 5 diverse and internally consistent synthetic users
for the following product research experiment.

PRODUCT:
{product.product_name}

DESCRIPTION:
{product.product_description}

FEATURES:
{", ".join(product.features)}

TARGET MARKET:
{product.target_market}

RESEARCH OBJECTIVE:
{product.research_objective}

Requirements:
- Generate exactly 5 personas.
- Personas must be meaningfully different from each other.
- Keep age, occupation, goals, behavior, motivations and concerns logically consistent.
- Personas must belong to the given target market.
- Their opinions should be based only on the provided product context.
- Do not invent product features.
- Do not make all personas positive about the product.
- Include different levels of product interest and price sensitivity.
- These are synthetic simulations, not real people.
"""

    return persona_llm.invoke(prompt)