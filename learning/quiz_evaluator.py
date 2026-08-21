def evaluate_answer(
    selected_answer: str,
    correct_answer: str,
) -> dict:
    """
    Evaluate a student's answer against the correct answer.
    """

    if not selected_answer.strip():
        raise ValueError(
            "Selected answer cannot be empty."
        )

    if not correct_answer.strip():
        raise ValueError(
            "Correct answer cannot be empty."
        )

    is_correct = (
        selected_answer.strip().lower()
        == correct_answer.strip().lower()
    )

    return {
        "selected_answer": selected_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
    }