from typing import List
from pydantic import BaseModel, Field


class ProductContext(BaseModel):
    product_name: str
    product_description: str
    features: List[str]
    target_market: str
    research_objective: str


class Persona(BaseModel):
    name: str
    age: int
    occupation: str
    location: str

    personality_traits: List[str]
    behavioral_patterns: List[str]

    goals: List[str]
    motivations: List[str]
    pain_points: List[str]

    price_sensitivity: str
    preferred_features: List[str]
    feature_concerns: List[str]

    product_interest: str
    willingness_to_pay: str


class PersonaList(BaseModel):
    personas: List[Persona] = Field(min_length=5, max_length=5)