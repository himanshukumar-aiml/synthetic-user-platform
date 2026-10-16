import re

from backend.llm import llm
from backend.models.persona import ProductContext, PersonaList

persona_llm = llm.with_structured_output(PersonaList)

NON_HUMAN_TERMS = (
    "alien", "aliens", "sentient robot", "robots", "robot audience",
    "planet", "planets", "dinosaur", "dinosaurs", "prehistoric predator",
    "animals", "animal audience",
)
FICTIONAL_AUDIENCE_MARKERS = (
    "fictional", "non-human", "nonhuman", "fantasy characters",
    "roleplay audience", "imaginary users",
)


def validate_product_input(product: ProductContext) -> None:
    """Reject obvious invalid inputs before persona generation."""
    fields = {
        "Product name": product.product_name,
        "Product description": product.product_description,
        "Target market": product.target_market,
        "Research objective": product.research_objective,
    }
    for label, value in fields.items():
        if not value or not value.strip():
            raise ValueError(f"{label} is required.")

    if not product.features or not any(feature.strip() for feature in product.features):
        raise ValueError("Please provide at least one product feature.")

    combined = " ".join([
        product.product_name, product.product_description,
        product.target_market, product.research_objective, *product.features
    ]).lower()
    if re.search(r"\b(asdfghjkl|qwerty12345|nothing works)\b", combined):
        raise ValueError(
            "Some input appears to be random or meaningless text. Please provide clear research details."
        )

    target = product.target_market.lower()
    has_non_human_target = any(term in target for term in NON_HUMAN_TERMS)
    explicitly_fictional = any(marker in target for marker in FICTIONAL_AUDIENCE_MARKERS)
    if has_non_human_target and not explicitly_fictional:
        raise ValueError(
            "The target market appears to include non-human or fictional audiences. "
            "Enter a real human customer group, or explicitly label the audience as fictional/non-human."
        )

    product_text = (
        product.product_name + " " + product.product_description + " " +
        " ".join(product.features)
    ).lower()
    age_match = re.search(r"\b(?:aged|ages)\s*(\d{1,3})\s*[-–to]+\s*(\d{1,3})\b", target)
    if age_match:
        min_age, max_age = int(age_match.group(1)), int(age_match.group(2))
        if min_age > max_age or max_age > 120:
            raise ValueError("The target-market age range is invalid.")
        finance_terms = (
            "stock trading", "trading platform", "derivatives",
            "investment", "high-frequency trading"
        )
        if max_age <= 7 and any(term in product_text for term in finance_terms):
            raise ValueError(
                "The target market appears incompatible with this financial product. "
                "Please review the intended users."
            )


def validate_generated_personas(product: ProductContext, result: PersonaList) -> None:
    """Reject impossible ages and personas outside an explicitly stated age range."""
    if len(result.personas) != 5:
        raise ValueError(
            f"The model returned {len(result.personas)} personas instead of 5. Please try again."
        )

    target = product.target_market.lower()
    age_match = re.search(r"\b(?:aged|ages)\s*(\d{1,3})\s*[-–to]+\s*(\d{1,3})\b", target)
    age_range = (int(age_match.group(1)), int(age_match.group(2))) if age_match else None

    for persona in result.personas:
        if not 0 <= persona.age <= 120:
            raise ValueError(
                f"Unrealistic age ({persona.age}) generated for {persona.name}. "
                "The personas were not displayed. Please try again."
            )

        if age_range and not age_range[0] <= persona.age <= age_range[1]:
            raise ValueError(
                f"{persona.name} (age {persona.age}) is outside the target-market age range "
                f"{age_range[0]}–{age_range[1]}. The personas were not displayed. Please try again."
            )

        details = " ".join([
            persona.occupation, persona.location,
            *persona.personality_traits, *persona.goals, *persona.motivations
        ]).lower()
        if any(term in details for term in NON_HUMAN_TERMS) and not any(
            marker in target for marker in FICTIONAL_AUDIENCE_MARKERS
        ):
            raise ValueError(
                f"The model generated a potentially non-human persona ({persona.name}) "
                "for a real-world target market. The personas were not displayed."
            )


def generate_personas(product: ProductContext) -> PersonaList:
    validate_product_input(product)

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
- Treat the target market as a strict constraint, not inspiration.
- Unless fictional/non-human roleplay is explicitly requested, generate realistic human customers only.
- If an age range is specified, every persona must fall inside it.
- Every human persona must have a plausible age between 0 and 120.
- Base opinions on the provided product context and do not invent product features.
- Do not make all personas positive about the product.
- Include different levels of product interest and price sensitivity.
- These are synthetic simulations, not real people.
"""

    result = persona_llm.invoke(prompt)
    validate_generated_personas(product, result)
    return result
