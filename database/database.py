import sqlite3
from pathlib import Path
import json


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file
DB_PATH = BASE_DIR / "data" / "synthetic_users.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # Allows accessing columns by name
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Research experiments
    # Would-use product scores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_id INTEGER NOT NULL,
        persona_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        decision TEXT NOT NULL,
        reasoning TEXT NOT NULL,

        FOREIGN KEY (experiment_id)
        REFERENCES experiments(id),

        FOREIGN KEY (persona_id)
        REFERENCES personas(id)
        )
        """)

    # Generated personas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            occupation TEXT,
            location TEXT,
            personality_traits TEXT,
            behavioral_patterns TEXT,
            goals TEXT,
            motivations TEXT,
            pain_points TEXT,
            price_sensitivity TEXT,
            preferred_features TEXT,
            feature_concerns TEXT,
            product_interest TEXT,
            willingness_to_pay TEXT,

            FOREIGN KEY (experiment_id)
            REFERENCES experiments(id)
        )
    """)

    # Survey responses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            persona_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (experiment_id)
            REFERENCES experiments(id),

            FOREIGN KEY (persona_id)
            REFERENCES personas(id)
        )
    """)

    # Interview conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            persona_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (experiment_id)
            REFERENCES experiments(id),

            FOREIGN KEY (persona_id)
            REFERENCES personas(id)
        )
    """)

    # Generated research insights
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (experiment_id)
            REFERENCES experiments(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")

def create_experiment(
    product_name,
    product_description,
    features,
    target_market,
    research_objective
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO experiments (
            product_name,
            product_description,
            features,
            target_market,
            research_objective
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product_name,
            product_description,
            json.dumps(features),
            target_market,
            research_objective
        )
    )

    experiment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return experiment_id

def create_persona(experiment_id, persona):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO personas (
            experiment_id,
            name,
            age,
            occupation,
            location,
            personality_traits,
            behavioral_patterns,
            goals,
            motivations,
            pain_points,
            price_sensitivity,
            preferred_features,
            feature_concerns,
            product_interest,
            willingness_to_pay
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            experiment_id,
            persona.name,
            persona.age,
            persona.occupation,
            persona.location,
            ", ".join(persona.personality_traits),
            ", ".join(persona.behavioral_patterns),
            ", ".join(persona.goals),
            ", ".join(persona.motivations),
            ", ".join(persona.pain_points),
            persona.price_sensitivity,
            ", ".join(persona.preferred_features),
            ", ".join(persona.feature_concerns),
            persona.product_interest,
            persona.willingness_to_pay
        )
    )

    persona_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return persona_id

def save_survey_response(
    experiment_id,
    persona_id,
    question,
    answer
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO survey_responses (
            experiment_id,
            persona_id,
            question,
            answer
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            experiment_id,
            persona_id,
            question,
            answer
        )
    )

    response_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return response_id
def save_interview_message(
    experiment_id,
    persona_id,
    role,
    message
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO interviews (
            experiment_id,
            persona_id,
            role,
            message
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            experiment_id,
            persona_id,
            role,
            message
        )
    )

    message_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return message_id
def save_insight(experiment_id, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO insights (
            experiment_id,
            content
        )
        VALUES (?, ?)
        """,
        (
            experiment_id,
            content
        )
    )

    insight_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return insight_id
def save_product_score(
    experiment_id,
    persona_id,
    score,
    decision,
    reasoning
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO product_scores (
            experiment_id,
            persona_id,
            score,
            decision,
            reasoning
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            experiment_id,
            persona_id,
            score,
            decision,
            reasoning
        )
    )

    score_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return score_id

