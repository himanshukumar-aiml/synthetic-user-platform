import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from backend.agents.persona_agent import generate_personas
from backend.models.persona import ProductContext


st.set_page_config(
    page_title="Synthetic User Lab",
    page_icon="🧠",
    layout="wide"
)


st.title("🧠 Synthetic User Lab")
st.caption("AI-powered synthetic user research platform")

st.divider()

st.header("Create Research Experiment")

product_name = st.text_input(
    "Product Name",
    placeholder="e.g. AI Fitness App"
)

product_description = st.text_area(
    "Product Description",
    placeholder="Describe your product..."
)

features_text = st.text_area(
    "Product Features",
    placeholder="Enter one feature per line"
)

target_market = st.text_area(
    "Target Market",
    placeholder="Describe your target users..."
)

research_objective = st.text_area(
    "Research Objective",
    placeholder="What do you want to learn from the synthetic users?"
)


if st.button("🚀 Generate Synthetic Users", use_container_width=True):

    if not all([
        product_name,
        product_description,
        features_text,
        target_market,
        research_objective
    ]):
        st.warning("Please fill in all fields.")

    else:
        features = [
            feature.strip()
            for feature in features_text.splitlines()
            if feature.strip()
        ]

        product = ProductContext(
            product_name=product_name,
            product_description=product_description,
            features=features,
            target_market=target_market,
            research_objective=research_objective
        )

        with st.spinner("Generating synthetic users..."):
            result = generate_personas(product)

        st.session_state["personas"] = result.personas
        st.success("5 synthetic users generated successfully!")


if "personas" in st.session_state:

    st.divider()
    st.header("Synthetic Personas")

    cols = st.columns(3)

    for index, persona in enumerate(st.session_state["personas"]):

        with cols[index % 3]:

            with st.container(border=True):

                st.subheader(persona.name)

                st.write(
                    f"**{persona.age} years • "
                    f"{persona.occupation}**"
                )

                st.write(f"📍 {persona.location}")

                st.write(
                    "**Personality:** "
                    + ", ".join(persona.personality_traits)
                )

                st.write(
                    "**Goals:** "
                    + ", ".join(persona.goals)
                )

                st.write(
                    "**Product Interest:** "
                    + persona.product_interest
                )