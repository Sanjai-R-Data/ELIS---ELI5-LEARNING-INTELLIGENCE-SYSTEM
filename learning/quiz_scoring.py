from backend.learning.quiz_evaluator import evaluate_answer


def calculate_quiz_score(
    answers: list[dict],
) -> dict:
    """
    Calculate the score for a completed quiz.

    Each answer must contain:

    {
        "selected_answer": "...",
        "correct_answer": "..."
    }
    """

    if not answers:
        raise ValueError(
            "At least one answer is required."
        )

    evaluated_answers = []
    correct_count = 0

    for answer in answers:
        if "selected_answer" not in answer:
            raise ValueError(
                "Each answer must contain selected_answer."
            )

        if "correct_answer" not in answer:
            raise ValueError(
                "Each answer must contain correct_answer."
            )

        result = evaluate_answer(
            selected_answer=answer["selected_answer"],
            correct_answer=answer["correct_answer"],
        )

        evaluated_answers.append(result)

        if result["is_correct"]:
            correct_count += 1

    total_questions = len(evaluated_answers)

    percentage = (
        correct_count / total_questions
    ) * 100

    return {
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": (
            total_questions - correct_count
        ),
        "score": correct_count,
        "percentage": round(percentage, 2),
        "answers": evaluated_answers,
    }