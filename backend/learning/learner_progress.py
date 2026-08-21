from backend.learning.learner_state import LearnerState
from backend.learning.quiz_scoring import calculate_quiz_score


def record_quiz_result(
    learner: LearnerState,
    topic: str,
    answers: list[dict],
) -> dict:
    """
    Score a completed quiz and update learner mastery.
    """

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    score = calculate_quiz_score(
        answers=answers,
    )

    mastery = learner.update_topic(
        topic=topic,
        percentage=score["percentage"],
    )

    return {
        "topic": topic,
        "score": score,
        "mastery": mastery,
    }