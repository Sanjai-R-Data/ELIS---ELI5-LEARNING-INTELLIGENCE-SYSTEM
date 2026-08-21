from backend.learning.learner_state import LearnerState


def get_adaptive_action(
    learner: LearnerState,
    topic: str,
) -> dict:
    """
    Decide what ELIS should do next based on
    the learner's current mastery of a topic.
    """

    if not topic.strip():
        raise ValueError(
            "Topic cannot be empty."
        )

    topic_state = learner.get_topic(topic)

    mastery = topic_state["mastery"]
    percentage = topic_state["percentage"]

    if mastery == "Needs Practice":
        action = "re_explain"

        next_steps = [
            "re_explain",
            "analogy",
            "easier_quiz",
        ]

        reason = (
            "The learner needs more practice with "
            "this topic."
        )

    elif mastery == "Developing":
        action = "analogy"

        next_steps = [
            "analogy",
            "more_practice",
            "quiz",
        ]

        reason = (
            "The learner has partial understanding "
            "and should reinforce the concept."
        )

    else:
        action = "advance"

        next_steps = [
            "advance",
            "challenge_quiz",
        ]

        reason = (
            "The learner has demonstrated strong "
            "understanding of this topic."
        )

    return {
        "topic": topic,
        "percentage": percentage,
        "mastery": mastery,
        "recommended_action": action,
        "next_steps": next_steps,
        "reason": reason,
    }