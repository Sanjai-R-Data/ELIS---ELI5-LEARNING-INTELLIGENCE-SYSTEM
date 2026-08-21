import json
import re

from backend.learning.class_levels import get_class_level
from backend.llm.ollama_client import generate_response


def build_quiz_prompt(
    class_id: int,
    source_text: str,
    topic: str,
    number_of_questions: int = 3,
) -> str:
    """
    Build a class-aware, source-grounded quiz prompt.
    """

    class_level = get_class_level(class_id)

    if not source_text.strip():
        raise ValueError("Source text cannot be empty.")

    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    if number_of_questions < 1:
        raise ValueError(
            "Number of questions must be at least 1."
        )

    if number_of_questions > 10:
        raise ValueError(
            "Number of questions cannot exceed 10."
        )

    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student has studied the following source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Topic:
{topic}

Create {number_of_questions} multiple-choice questions
to test the student's understanding of this topic.

Return ONLY valid JSON using exactly this structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "The exact correct option",
      "explanation": "A short explanation of why this answer is correct"
    }}
  ]
}}

Rules:
- Questions must be based primarily on the provided source material.
- Do not ask about information that is not supported by the source.
- Match the difficulty to {class_level["name"]}.
- Each question must have exactly 4 options.
- Only one option should be correct.
- The correct_answer must exactly match one of the options.
- Make incorrect options plausible but clearly incorrect.
- Do not make the correct answer obvious because of its length.
- Do not repeat the same question.
- Test understanding rather than simple word matching when possible.
- Keep explanations short and clear.
- Return JSON only.
- Do not use Markdown code fences.
"""

    return prompt.strip()


def clean_json_response(raw_response: str) -> str:
    """
    Remove harmless Markdown formatting from an LLM response.
    """

    response = raw_response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    return response.strip()


def generate_quiz(
    class_id: int,
    source_text: str,
    topic: str,
    number_of_questions: int = 3,
) -> dict:
    """
    Generate and validate a structured quiz.
    """

    prompt = build_quiz_prompt(
        class_id=class_id,
        source_text=source_text,
        topic=topic,
        number_of_questions=number_of_questions,
    )

    raw_response = generate_response(prompt)

    if not raw_response or not raw_response.strip():
        raise ValueError(
            "The AI model returned an empty quiz response."
        )

    cleaned_response = clean_json_response(raw_response)

    try:
        quiz = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Model returned invalid quiz JSON: {error}"
        ) from error

    if "questions" not in quiz:
        raise ValueError(
            "Quiz response is missing the questions field."
        )

    if not isinstance(quiz["questions"], list):
        raise ValueError(
            "Quiz questions must be a list."
        )

    if not quiz["questions"]:
        raise ValueError(
            "Quiz must contain at least one question."
        )

    for question in quiz["questions"]:
        if not isinstance(question, dict):
            raise ValueError(
                "Each quiz question must be an object."
            )

        required_fields = [
            "question",
            "options",
            "correct_answer",
            "explanation",
        ]

        for field in required_fields:
            if field not in question:
                raise ValueError(
                    f"Quiz question is missing: {field}"
                )

        if not isinstance(question["options"], list):
            raise ValueError(
                "Question options must be a list."
            )

        if len(question["options"]) != 4:
            raise ValueError(
                "Each question must have exactly 4 options."
            )

        if question["correct_answer"] not in question["options"]:
            raise ValueError(
                "correct_answer must exactly match one "
                "of the provided options."
            )

    return {
        "class_id": class_id,
        "topic": topic,
        "quiz": quiz,
    }