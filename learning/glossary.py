import json
import re

from backend.learning.class_levels import get_class_level
from backend.llm.ollama_client import generate_response


def build_glossary_prompt(
    class_id: int,
    source_text: str,
    topic: str = "",
) -> str:
    """
    Build a class-aware, source-grounded glossary prompt.
    """

    class_level = get_class_level(class_id)

    if not source_text.strip():
        raise ValueError("Source text cannot be empty.")

    if topic is not None and not topic.strip():
        raise ValueError("Topic cannot be empty.")

    topic_instruction = (
        f"""
The student selected this specific topic:
{topic}

Generate the glossary ONLY for this selected topic.
Do not choose a different topic from the textbook.
"""
        if topic and topic.strip()
        else
        """
Generate the glossary for the provided source material.
"""
    )

    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student is learning from this source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Identify the most important technical, difficult, or
subject-specific terms that a {class_level["name"]} student
should understand.

Return ONLY valid JSON using exactly this structure:

{{
  "terms": [
    {{
      "term": "Term",
      "definition": "Simple definition suitable for the student's class"
    }}
  ]
}}

Rules:
- Select 5 to 10 important terms when enough terms are available.
- Prefer terms that are important for understanding the source.
- Use the source material as the primary source.
- Definitions must be consistent with the source.
- Do not invent unsupported facts.
- Do not include ordinary everyday words.
- Keep definitions short and clear.
- Match the vocabulary and depth to {class_level["name"]}.
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


def generate_glossary(
    class_id: int,
    source_text: str,
    topic: str = "",
) -> dict:
    """
    Generate and validate a structured glossary.
    """

    prompt = build_glossary_prompt(
        class_id=class_id,
        source_text=source_text,
        topic=topic,
    )

    raw_response = generate_response(prompt)

    if not raw_response or not raw_response.strip():
        raise ValueError(
            "The AI model returned an empty glossary response."
        )

    cleaned_response = clean_json_response(raw_response)

    try:
        glossary = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Model returned invalid glossary JSON: {error}"
        ) from error

    if "terms" not in glossary:
        raise ValueError(
            "Glossary response is missing the terms field."
        )

    if not isinstance(glossary["terms"], list):
        raise ValueError(
            "Glossary terms must be a list."
        )

    for item in glossary["terms"]:
        if not isinstance(item, dict):
            raise ValueError(
                "Each glossary term must be an object."
            )

        if "term" not in item:
            raise ValueError(
                "Each glossary item requires a term."
            )

        if "definition" not in item:
            raise ValueError(
                "Each glossary item requires a definition."
            )

    return {
        "class_id": class_id,
        "topic": topic,
        "glossary": glossary,
    }