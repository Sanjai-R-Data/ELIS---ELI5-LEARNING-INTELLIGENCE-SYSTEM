import json
import re

from backend.learning.class_levels import get_class_level
from backend.llm.ollama_client import generate_response


def build_explanation_prompt(
    class_id: int,
    source_text: str,
    instruction: str,
) -> str:
    """
    Build a class-aware explanation prompt.
    """

    class_level = get_class_level(class_id)

    if not source_text.strip():
        raise ValueError(
            "Source text cannot be empty."
        )

    if not instruction.strip():
        raise ValueError(
            "Instruction cannot be empty."
        )

    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student is learning from the following source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Instruction:
{instruction}

Create a simple, accurate explanation appropriate
for the student's level.

Return ONLY valid JSON using exactly this structure:

{{
  "title": "Short title",
  "simple_explanation": "Simple explanation",
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ],
  "simple_example": "A simple example",
  "important_terms": [
    {{
      "term": "Term",
      "meaning": "Simple meaning"
    }}
  ]
}}

Rules:
- Base the explanation primarily on the provided source.
- Do not introduce unsupported facts.
- Match the explanation to the student's level.
- Use simple and clear language.
- Keep the explanation concise.
- Return JSON only.
- Do not use Markdown code fences.
"""

    return prompt.strip()


def clean_json_response(raw_response: str) -> str:
    """
    Remove Markdown code fences and surrounding whitespace
    from an LLM JSON response.
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


def generate_explanation(
    class_id: int,
    source_text: str,
    instruction: str,
) -> dict:
    """
    Generate and validate a structured explanation.
    """

    prompt = build_explanation_prompt(
        class_id=class_id,
        source_text=source_text,
        instruction=instruction,
    )

    raw_response = generate_response(prompt)

    if not raw_response or not raw_response.strip():
        raise ValueError(
            "The AI model returned an empty explanation."
        )

    cleaned_response = clean_json_response(
        raw_response
    )

    try:
        explanation = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:
        print("\n--- RAW MODEL RESPONSE ---")
        print(repr(raw_response))

        print("\n--- CLEANED JSON RESPONSE ---")
        print(cleaned_response)

        print("\n--- END DEBUG RESPONSE ---")

        raise ValueError(
            f"Model returned invalid JSON: {error}"
        ) from error

    required_fields = [
        "title",
        "simple_explanation",
        "key_points",
        "simple_example",
        "important_terms",
    ]

    for field in required_fields:
        if field not in explanation:
            raise ValueError(
                f"Explanation is missing field: {field}"
            )

    if not isinstance(
        explanation["key_points"],
        list,
    ):
        raise ValueError(
            "key_points must be a list."
        )

    if not isinstance(
        explanation["important_terms"],
        list,
    ):
        raise ValueError(
            "important_terms must be a list."
        )

    return explanation