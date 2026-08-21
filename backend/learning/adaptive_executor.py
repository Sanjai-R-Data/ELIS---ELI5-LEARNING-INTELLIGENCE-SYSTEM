from backend.learning.adaptive_engine import (
    get_adaptive_action,
)
from backend.learning.analogy import generate_analogy
from backend.learning.explanation import generate_explanation
from backend.learning.learner_state import LearnerState
from backend.learning.quiz import generate_quiz


def execute_adaptive_action(
    learner: LearnerState,
    class_id: int,
    topic: str,
    source_text: str,
) -> dict:
    """
    Execute the adaptive action selected for a learner.
    """

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    if not source_text.strip():
        raise ValueError(
            "Source text cannot be empty."
        )

    recommendation = get_adaptive_action(
        learner=learner,
        topic=topic,
    )

    action = recommendation["recommended_action"]

    if action == "re_explain":

        result = generate_explanation(
            class_id=class_id,
            source_text=source_text,
            instruction=(
                f"Re-explain the topic '{topic}' "
                "in a simpler way because the learner "
                "needs more practice."
            ),
        )

    elif action == "analogy":

        result = generate_analogy(
            class_id=class_id,
            source_text=source_text,
            concept=topic,
        )

    elif action == "advance":

        result = {
            "message": (
                f"The learner has demonstrated strong "
                f"understanding of {topic} and is ready "
                "to move forward."
            )
        }

    else:

        raise ValueError(
            f"Unsupported adaptive action: {action}"
        )

    return {
        "topic": topic,
        "mastery": recommendation["mastery"],
        "percentage": recommendation["percentage"],
        "action": action,
        "recommendation": recommendation,
        "result": result,
    }


def generate_adaptive_quiz(
    learner: LearnerState,
    class_id: int,
    topic: str,
    source_text: str,
) -> dict:
    """
    Generate a quiz appropriate for the learner's
    current mastery level.
    """

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    if not source_text.strip():
        raise ValueError(
            "Source text cannot be empty."
        )

    recommendation = get_adaptive_action(
        learner=learner,
        topic=topic,
    )

    mastery = recommendation["mastery"]

    if mastery == "Needs Practice":
        difficulty_instruction = (
            "Create easier questions that focus on "
            "fundamental understanding."
        )

    elif mastery == "Developing":
        difficulty_instruction = (
            "Create moderate questions that reinforce "
            "the important concepts."
        )

    else:
        difficulty_instruction = (
            "Create challenging questions that test "
            "deeper understanding."
        )

    quiz = generate_quiz(
        class_id=class_id,
        source_text=source_text,
        topic=topic,
        number_of_questions=3,
    )

    return {
        "topic": topic,
        "mastery": mastery,
        "percentage": recommendation["percentage"],
        "difficulty_instruction": difficulty_instruction,
        "quiz": quiz,
    }