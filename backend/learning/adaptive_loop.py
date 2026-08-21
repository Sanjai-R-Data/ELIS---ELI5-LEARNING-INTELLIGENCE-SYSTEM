from backend.learning.adaptive_engine import (
    get_adaptive_action,
)
from backend.learning.adaptive_executor import (
    execute_adaptive_action,
)
from backend.learning.learning_progress import (
    record_quiz_result,
)
from backend.learning.learner_state import LearnerState


def run_adaptive_cycle(
    learner: LearnerState,
    class_id: int,
    topic: str,
    source_text: str,
    answers: list[dict],
) -> dict:
    """
    Run one complete adaptive learning cycle.

    Flow:

    Quiz answers
        ↓
    Update learner state
        ↓
    Calculate mastery
        ↓
    Decide next action
        ↓
    Execute intervention
    """

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    if not source_text.strip():
        raise ValueError(
            "Source text cannot be empty."
        )

    if not answers:
        raise ValueError(
            "Answers cannot be empty."
        )

    # -------------------------------------------------
    # STEP 1: Record the quiz result
    # -------------------------------------------------

    progress = record_quiz_result(
        learner=learner,
        topic=topic,
        answers=answers,
    )

    # -------------------------------------------------
    # STEP 2: Ask the adaptive engine what to do next
    # -------------------------------------------------

    recommendation = get_adaptive_action(
        learner=learner,
        topic=topic,
    )

    # -------------------------------------------------
    # STEP 3: Execute the recommended intervention
    # -------------------------------------------------

    intervention = execute_adaptive_action(
        learner=learner,
        class_id=class_id,
        topic=topic,
        source_text=source_text,
    )

    # -------------------------------------------------
    # STEP 4: Return the complete adaptive cycle
    # -------------------------------------------------

    return {
        "topic": topic,
        "progress": progress,
        "mastery": recommendation["mastery"],
        "percentage": recommendation["percentage"],
        "recommended_action": recommendation[
            "recommended_action"
        ],
        "next_steps": recommendation[
            "next_steps"
        ],
        "reason": recommendation["reason"],
        "intervention": intervention,
    }