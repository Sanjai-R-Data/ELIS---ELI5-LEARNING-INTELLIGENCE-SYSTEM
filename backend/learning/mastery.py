def calculate_mastery(
    score: int,
    total: int,
) -> dict:
    """
    Calculate simple mastery for a completed quiz.

    Categories:
    0–39%   -> Needs Practice
    40–69%  -> Developing
    70–100% -> Strong
    """

    if total <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    if score < 0:
        raise ValueError(
            "Score cannot be negative."
        )

    if score > total:
        raise ValueError(
            "Score cannot be greater than total questions."
        )

    percentage = round(
        (score / total) * 100
    )

    if percentage < 40:
        status = "Needs Practice"
        message = (
            "Review the learning material and "
            "try the quiz again."
        )

    elif percentage < 70:
        status = "Developing"
        message = (
            "You are making progress. "
            "A little more practice can strengthen "
            "your understanding."
        )

    else:
        status = "Strong"
        message = (
            "You have a strong understanding "
            "of this topic."
        )

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "status": status,
        "message": message,
    }