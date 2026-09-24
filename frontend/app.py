import sys
from pathlib import Path
import html

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from backend.agents.persona_agent import generate_personas
from backend.models.persona import ProductContext


# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="Synthetic User Lab",
    page_icon="🧠",
    layout="wide"
)


# --------------------------------
# LOAD CSS
# --------------------------------

css_path = Path(__file__).parent / "styles.css"

with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# --------------------------------
# SESSION STATE
# --------------------------------

if "personas" not in st.session_state:
    st.session_state.personas = []


# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0 25px 0;">
            <div style="font-size:42px;">🧠</div>
            <h2 style="margin:5px 0;">Synthetic User Lab</h2>
            <p style="color:#94a3b8; font-size:13px;">
                AI-powered user research
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Research")

    st.button("➕ New Research", use_container_width=True)
    st.button("👥 Personas", use_container_width=True)
    st.button("🎤 Interviews", use_container_width=True)
    st.button("📋 Surveys", use_container_width=True)
    st.button("💡 Insights", use_container_width=True)
    st.button("📄 Reports", use_container_width=True)

    st.divider()

    st.caption("Local AI")
    st.caption("🟢 Ollama • Qwen3:8B")


# --------------------------------
# HERO
# --------------------------------

st.html(
    """
    <div class="hero">
        <div class="hero-badge">
            🧪 Synthetic User Research Platform
        </div>

        <div class="hero-title">
            Turn product ideas into
            <span style="color:#818cf8;"> synthetic users.</span>
        </div>

        <div class="hero-subtitle">
            Create AI-powered personas and simulate product research
            before talking to real users.
        </div>
    </div>
    """
)


# --------------------------------
# RESEARCH SETUP
# --------------------------------

st.markdown(
    """
    <div class="section-title">
        Create Research Experiment
    </div>

    <div class="section-subtitle">
        Define your product and target audience. The AI will generate
        synthetic users based on your research context.
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------
# DEMO / CUSTOM MODE
# --------------------------------

mode_col1, mode_col2 = st.columns([1, 3])

with mode_col1:

    mode = st.radio(
        "Research Type",
        ["Custom Product", "Demo Product"],
        index=0
    )


# --------------------------------
# PRODUCT DATA
# --------------------------------

if mode == "Demo Product":

    product_name = "AI Fitness App"

    product_description = (
        "An AI-powered fitness application that provides "
        "personalized workouts, nutrition tracking and an AI fitness assistant."
    )

    features = [
        "Personalized workout plans",
        "10-minute quick workouts",
        "Calorie and nutrition tracking",
        "AI fitness assistant",
        "Progress tracking",
        "Premium subscription at ₹299/month"
    ]

    target_market = (
        "College students and young working professionals aged 18–30"
    )

    research_objective = (
        "Understand user motivations, concerns, feature preferences "
        "and willingness to pay."
    )

    st.info("🏋️ Demo product loaded: AI Fitness App")


else:

    # --------------------------------
    # CUSTOM PRODUCT FORM
    # --------------------------------

    with st.container(border=True):

        st.markdown("### 📦 Product Information")

        col1, col2 = st.columns(2)

        with col1:

            product_name = st.text_input(
                "Product Name",
                placeholder="e.g. AI Fitness App"
            )

            product_description = st.text_area(
                "Product Description",
                placeholder="Describe what your product does...",
                height=130
            )

        with col2:

            features_text = st.text_area(
                "Product Features",
                placeholder=(
                    "Enter one feature per line\n\n"
                    "Personalized recommendations\n"
                    "AI assistant\n"
                    "Progress tracking"
                ),
                height=130
            )

            target_market = st.text_area(
                "Target Market",
                placeholder=(
                    "Describe your target users...\n"
                    "Example: College students aged 18–25"
                ),
                height=130
            )

        st.markdown("### 🎯 Research Objective")

        research_objective = st.text_area(
            "What do you want to learn?",
            placeholder=(
                "Example: Understand user needs, concerns and "
                "willingness to pay."
            ),
            height=100
        )


# --------------------------------
# GENERATE BUTTON
# --------------------------------

st.markdown("<br>", unsafe_allow_html=True)

generate = st.button(
    "✨ Generate 5 Synthetic Users",
    use_container_width=True
)


# --------------------------------
# GENERATE PERSONAS
# --------------------------------

if generate:

    if mode == "Custom Product":

        if not all([
            product_name,
            product_description,
            features_text,
            target_market,
            research_objective
        ]):

            st.warning(
                "Please complete all research fields before generating personas."
            )

            st.stop()

        features = [
            feature.strip()
            for feature in features_text.splitlines()
            if feature.strip()
        ]

    else:

        features = features


    product = ProductContext(
        product_name=product_name,
        product_description=product_description,
        features=features,
        target_market=target_market,
        research_objective=research_objective
    )

    with st.spinner("Creating diverse synthetic users..."):

        result = generate_personas(product)

    st.session_state.personas = result.personas

    st.success("5 synthetic personas generated successfully!")


# --------------------------------
# PERSONAS
# --------------------------------

if st.session_state.personas:

    st.divider()

    st.markdown(
        """
        <div class="section-title">
            👥 Synthetic Personas
        </div>

        <div class="section-subtitle">
            AI-generated users based on your research context.
        </div>
        """,
        unsafe_allow_html=True
    )

    personas = st.session_state.personas

    for row_start in range(0, len(personas), 3):

        cols = st.columns(3)

        for col, persona in zip(
            cols,
            personas[row_start:row_start + 3]
        ):

            with col:

                traits = ", ".join(persona.personality_traits[:3])
                goals = ", ".join(persona.goals[:2])

                st.markdown(
                    f"""
                    <div class="persona-card">

                        <div style="font-size:32px; margin-bottom:10px;">
                            👤
                        </div>

                        <div class="persona-name">
                            {html.escape(persona.name)}
                        </div>

                        <div class="persona-meta">
                            {persona.age} years •
                            {html.escape(persona.occupation)}
                            <br>
                            📍 {html.escape(persona.location)}
                        </div>

                        <div class="persona-label">
                            Personality
                        </div>

                        <div class="persona-value">
                            {html.escape(traits)}
                        </div>

                        <div class="persona-label">
                            Goals
                        </div>

                        <div class="persona-value">
                            {html.escape(goals)}
                        </div>

                        <div class="persona-label">
                            Product Interest
                        </div>

                        <div class="persona-value">
                            {html.escape(persona.product_interest)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )