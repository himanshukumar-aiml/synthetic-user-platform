import sys
from pathlib import Path
import html

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from backend.agents.persona_agent import generate_personas
from backend.models.persona import ProductContext
from database.database import (
    create_experiment,
    create_persona,
    save_survey_response,
    save_interview_message,
    save_insight
)


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

if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

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
    st.session_state.product_name = product.product_name
    st.session_state.research_objective = product.research_objective
    experiment_id = create_experiment(
    product_name=product.product_name,
    product_description=product.product_description,
    features=product.features,
    target_market=product.target_market,
    research_objective=product.research_objective
)

    st.session_state.experiment_id = experiment_id
    persona_ids = []

    for persona in result.personas:
        persona_id = create_persona(
            experiment_id=experiment_id,
            persona=persona
        )
        persona_ids.append(persona_id)

    st.session_state.persona_ids = persona_ids

    st.success("5 synthetic personas generated successfully!")


# --------------------------------
# PERSONA DASHBOARD
# --------------------------------

if st.session_state.personas:

    st.divider()

    st.html(
        """
        <div class="section-title">
            👥 Synthetic Personas
        </div>

        <div class="section-subtitle">
            Explore the AI-generated users created for this research experiment.
        </div>
        """
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
                motivations = ", ".join(persona.motivations[:2])

                st.html(
                    f"""
                    <div class="persona-card">

                        <div style="font-size:36px;">
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
                            Motivation
                        </div>

                        <div class="persona-value">
                            {html.escape(motivations)}
                        </div>

                        <div class="persona-label">
                            Product Interest
                        </div>

                        <div class="persona-value">
                            {html.escape(persona.product_interest)}
                        </div>

                    </div>
                    """
                )

                if st.button(
                    f"🎤 Interview with {persona.name}",
                    key=f"interview_{row_start}_{persona.name}",
                    use_container_width=True
                ):
                    st.session_state.selected_persona = persona
                    st.session_state.chat_messages = []
                    st.rerun()
# --------------------------------
# INTERVIEW MODE
# --------------------------------

if st.session_state.selected_persona:

    persona = st.session_state.selected_persona

    st.divider()

    st.html(
        f"""
        <div class="hero">
            <div class="hero-badge">
                🎤 Interview Mode
            </div>

            <div class="hero-title">
                Interview with {html.escape(persona.name)}
            </div>

            <div class="hero-subtitle">
                {persona.age} years •
                {html.escape(persona.occupation)} •
                {html.escape(persona.location)}
            </div>
        </div>
        """
    )

    if st.button("← Back to Personas"):
        st.session_state.selected_persona = None
        st.session_state.chat_messages = []
        st.rerun()

    st.markdown("### Conversation")

    for message in st.session_state.chat_messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input(
        f"Ask {persona.name} a question..."
    )

    if user_message:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_message
        })
        persona_index = st.session_state.personas.index(persona)

        persona_id = st.session_state.persona_ids[persona_index]

        save_interview_message(
            experiment_id=st.session_state.experiment_id,
            persona_id=persona_id,
            role="user",
            message=user_message
)

        with st.chat_message("user"):
            st.write(user_message)

        from backend.agents.interview_agent import interview_persona

        with st.chat_message("assistant"):

            with st.spinner("Persona is thinking..."):

                response = interview_persona(
                    persona,
                    st.session_state.chat_messages[:-1],
                    user_message
                )

            st.write(response)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })
        save_interview_message(
            experiment_id=st.session_state.experiment_id,
            persona_id=persona_id,
            role="assistant",
            message=response
        )
# --------------------------------
# SURVEY MODE
# --------------------------------

st.divider()

st.html(
    """
    <div class="section-title">
        📋 Survey Mode
    </div>

    <div class="section-subtitle">
        Ask the same research question to all generated personas.
    </div>
    """
)

if st.session_state.personas:

    survey_question = st.text_area(
        "Survey Question",
        placeholder="Example: What would motivate you to use this product regularly?",
        height=100,
        key="survey_question"
    )

    if st.button(
        "📋 Run Survey",
        use_container_width=True
    ):

        if not survey_question.strip():

            st.warning("Please enter a survey question.")

        else:

            from backend.agents.survey_agent import survey_persona

            survey_results = []

            with st.spinner("Collecting responses from all personas..."):

                for persona in st.session_state.personas:

                    answer = survey_persona(
                        persona,
                        survey_question
                    )
                    persona_index = st.session_state.personas.index(persona)

                    persona_id = st.session_state.persona_ids[persona_index]
    
                    save_survey_response(
                    experiment_id=st.session_state.experiment_id,
                    persona_id=persona_id,
                    question=survey_question,
                    answer=answer
)

                    survey_results.append({
                        "persona": persona,
                        "answer": answer
                    })

            st.session_state.survey_results = survey_results

            st.success("Survey completed successfully!")


    # --------------------------------
    # SURVEY RESULTS
    # --------------------------------

    if "survey_results" in st.session_state:

        if st.session_state.survey_results:

            st.markdown("### Survey Responses")

            for result in st.session_state.survey_results:

                persona = result["persona"]

                st.html(
                    f"""
                    <div class="persona-card">

                        <div class="persona-name">
                            👤 {html.escape(persona.name)}
                        </div>

                        <div class="persona-meta">
                            {persona.age} years •
                            {html.escape(persona.occupation)}
                        </div>

                        <div class="persona-label">
                            Response
                        </div>

                        <div class="persona-value">
                            {html.escape(result["answer"])}
                        </div>

                    </div>
                    """
                )

else:

    st.info(
        "Generate synthetic personas first to use Survey Mode."
    )

# --------------------------------
# INSIGHTS
# --------------------------------

st.divider()

st.html(
    """
    <div class="section-title">
        💡 Research Insights
    </div>

    <div class="section-subtitle">
        Extract meaningful patterns from synthetic user responses.
    </div>
    """
)

if "survey_results" in st.session_state and st.session_state.survey_results:

    if st.button(
        "✨ Extract Research Insights",
        use_container_width=True
    ):

        from backend.agents.insight_agent import extract_insights

        with st.spinner("Analyzing survey responses..."):

            insights = extract_insights(
                st.session_state.product_name,
                st.session_state.research_objective,
                st.session_state.survey_results
            )

        st.session_state.insights = insights

        save_insight(
                experiment_id=st.session_state.experiment_id,
                content=insights
)

    if "insights" in st.session_state and st.session_state.insights:

        st.markdown("### Research Findings")

        st.markdown(st.session_state.insights)

else:

    st.info(
        "Run a survey first to generate research insights."
    )

# --------------------------------
# PDF REPORT
# --------------------------------

if "insights" in st.session_state and st.session_state.insights:

    st.divider()

    st.html(
        """
        <div class="section-title">
            📄 Research Report
        </div>

        <div class="section-subtitle">
            Download the complete synthetic user research report.
        </div>
        """
    )

    from backend.services.report_service import create_research_report

    pdf_data = create_research_report(
        st.session_state.product_name,
        st.session_state.research_objective,
        st.session_state.survey_results,
        st.session_state.insights
    )

    st.download_button(
        label="📄 Download Research Report",
        data=pdf_data,
        file_name="synthetic_user_research_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )