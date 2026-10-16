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
    save_insight,
    save_product_score
)
from backend.agents.scoring_agent import score_persona


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

if "product_scores" not in st.session_state:
    st.session_state.product_scores = []



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

    with st.spinner("Validating input and creating synthetic users..."):

        try:
            result = generate_personas(product)
        except ValueError as error:
            st.error(f"Input/persona validation failed: {error}")
            st.stop()
        except Exception:
            st.error(
                "Persona generation failed or returned invalid output. "
                "Please review your inputs and try again."
            )
            st.stop()

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
# PRODUCT SCORING
# --------------------------------

st.divider()

st.html(
    """
    <div class="section-title">
        🎯 Would You Use This Product?
    </div>

    <div class="section-subtitle">
        Evaluate each synthetic persona's simulated willingness to use the product.
    </div>
    """
)

if st.session_state.personas:

    if st.button(
        "🎯 Evaluate Product Preference",
        use_container_width=True
    ):

        scores = []

        with st.spinner("Evaluating synthetic user preferences..."):

            for persona in st.session_state.personas:

                result = score_persona(
                    persona=persona,
                    product_name=st.session_state.product_name,
                    research_objective=st.session_state.research_objective
                )

                # Convert score into decision
                if result.score >= 70:
                    decision = "Yes"
                elif result.score >= 40:
                    decision = "Maybe"
                else:
                    decision = "No"

                persona_index = st.session_state.personas.index(persona)
                persona_id = st.session_state.persona_ids[persona_index]

                # Save score to database
                save_product_score(
                    experiment_id=st.session_state.experiment_id,
                    persona_id=persona_id,
                    score=result.score,
                    decision=decision,
                    reasoning=result.reasoning
                )

                scores.append({
                    "persona": persona,
                    "score": result.score,
                    "decision": decision,
                    "reasoning": result.reasoning
                })

        st.session_state.product_scores = scores

        st.success("Product preference evaluation completed!")


# --------------------------------
# SCORE RESULTS
# --------------------------------

if st.session_state.product_scores:

    st.markdown("### Persona Preference Results")

    for result in st.session_state.product_scores:

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
                    Synthetic Preference Score
                </div>

                <div class="persona-value">
                    <strong>{result["score"]}/100</strong>
                </div>

                <div class="persona-label">
                    Decision
                </div>

                <div class="persona-value">
                    <strong>{result["decision"]}</strong>
                </div>

                <div class="persona-label">
                    Reasoning
                </div>

                <div class="persona-value">
                    {html.escape(result["reasoning"])}
                </div>

            </div>
            """
        )

    st.caption(
        "Note: These scores represent simulated preferences of AI-generated "
        "personas and are not predictions of real-world customer behavior."
    )
# --------------------------------
# PERSONA SEGMENT SUMMARY
# --------------------------------

st.markdown("### 📊 Persona Segment Summary")

high_interest = [
    r for r in st.session_state.product_scores
    if r["score"] >= 70
]

moderate_interest = [
    r for r in st.session_state.product_scores
    if 40 <= r["score"] < 70
]

low_interest = [
    r for r in st.session_state.product_scores
    if r["score"] < 40
]


def average_score(results):
    if not results:
        return 0
    return round(
        sum(r["score"] for r in results) / len(results),
        1
    )


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "High Interest",
        len(high_interest),
        f"Avg: {average_score(high_interest)}"
    )

with col2:
    st.metric(
        "Moderate Interest",
        len(moderate_interest),
        f"Avg: {average_score(moderate_interest)}"
    )

with col3:
    st.metric(
        "Low Interest",
        len(low_interest),
        f"Avg: {average_score(low_interest)}"
    )
# --------------------------------
# INSIGHTS & EXPERIMENT DASHBOARD
# --------------------------------

st.divider()
st.markdown("## 📊 Insights & Experiment Results Dashboard")
st.caption(
    "Dashboard patterns are derived from synthetic AI-generated responses. "
    "They are exploratory signals, not evidence about real-world customers."
)

survey_results_for_dashboard = st.session_state.get("survey_results", [])
product_scores_for_dashboard = st.session_state.get("product_scores", [])

if survey_results_for_dashboard:
    # Simple keyword-based theme clustering from actual survey response text.
    theme_keywords = {
        "Ease of use": ["easy", "simple", "intuitive", "confusing", "complicated", "user-friendly"],
        "Price and value": ["price", "cost", "expensive", "cheap", "afford", "subscription", "value"],
        "Features and functionality": ["feature", "function", "tool", "custom", "personal", "option"],
        "Trust and privacy": ["privacy", "data", "secure", "trust", "safe", "personal information"],
        "Convenience and time": ["time", "quick", "convenient", "busy", "schedule", "fast"],
        "Accuracy and reliability": ["accurate", "accuracy", "reliable", "wrong", "error", "correct"]
    }
    theme_counts = {theme: 0 for theme in theme_keywords}
    for row in survey_results_for_dashboard:
        answer_text = str(row.get("answer", "")).lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in answer_text for keyword in keywords):
                theme_counts[theme] += 1

    positive_words = ["love", "great", "good", "helpful", "useful", "easy", "excited", "excellent", "benefit", "convenient", "recommend", "interested"]
    negative_words = ["hate", "bad", "poor", "difficult", "hard", "expensive", "concern", "worry", "worried", "confusing", "frustrat", "not use", "won't", "would not", "unreliable"]
    sentiment_counts = {"Positive": 0, "Neutral / mixed": 0, "Negative": 0}
    sentiment_by_persona = []

    for row in survey_results_for_dashboard:
        answer = str(row.get("answer", ""))
        lowered = answer.lower()
        positive_hits = sum(1 for word in positive_words if word in lowered)
        negative_hits = sum(1 for word in negative_words if word in lowered)
        if positive_hits > negative_hits:
            sentiment = "Positive"
        elif negative_hits > positive_hits:
            sentiment = "Negative"
        else:
            sentiment = "Neutral / mixed"
        sentiment_counts[sentiment] += 1
        sentiment_by_persona.append((row.get("persona"), answer, sentiment))

    theme_col, sentiment_col = st.columns(2)
    with theme_col:
        st.markdown("### 🧩 Theme Clusters")
        st.caption("Keyword-based counts: number of responses mentioning each theme; one response can match multiple themes.")
        nonzero_themes = {key: value for key, value in theme_counts.items() if value > 0}
        if nonzero_themes:
            st.bar_chart(nonzero_themes, horizontal=True)
        else:
            st.info("No common theme keywords were detected. Review the responses directly.")

    with sentiment_col:
        st.markdown("### 💬 Sentiment Breakdown")
        st.caption("Approximate keyword-based classification, not an ML sentiment model.")
        st.bar_chart(sentiment_counts)
        st.write("**Sentiment by persona**")
        for persona, answer, sentiment in sentiment_by_persona:
            name = getattr(persona, "name", "Persona")
            st.write(f"- **{name}:** {sentiment}")

    st.markdown("### 🗣️ Key Persona Quotes")
    st.caption("Short excerpts copied from the generated survey responses.")
    for persona, answer, sentiment in sentiment_by_persona:
        name = getattr(persona, "name", "Persona")
        excerpt = " ".join(str(answer).split())
        if len(excerpt) > 260:
            excerpt = excerpt[:257].rsplit(" ", 1)[0] + "..."
        with st.container(border=True):
            st.markdown(f"**{name}** · {sentiment}")
            st.write(f'“{excerpt}”')
else:
    st.info("Run a survey to populate theme clusters, sentiment, and persona quotes.")

if product_scores_for_dashboard:
    st.markdown("### 🎯 Product Validation Scores")
    score_chart_data = {
        getattr(result.get("persona"), "name", f"Persona {index + 1}"): result.get("score", 0)
        for index, result in enumerate(product_scores_for_dashboard)
    }
    st.bar_chart(score_chart_data, horizontal=True)
    st.caption("Scores represent simulated persona preferences only; they do not predict real-world adoption.")
else:
    st.info("Run Evaluate Product Preference to display persona validation scores.")

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
        st.session_state.insights,
        product_scores=st.session_state.product_scores
    )

    st.download_button(
        label="📄 Download Research Report",
        data=pdf_data,
        file_name="synthetic_user_research_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )