import json
import re

from backend.learning.class_levels import get_class_level
from backend.llm.ollama_client import generate_response


def build_analogy_prompt(
    class_id: int,
    source_text: str,
    concept: str,
) -> str:
    """
    Build a class-aware, source-grounded analogy prompt.
    """

    class_level = get_class_level(class_id)

    if not source_text.strip():
        raise ValueError("Source text cannot be empty.")

    if not concept.strip():
        raise ValueError("Concept cannot be empty.")

    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student is learning from this source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Concept to explain:
{concept}

Create ONE simple real-world analogy that helps a
{class_level["name"]} student understand this concept.

Return ONLY valid JSON using exactly this structure:

{{
  "concept": "The concept being explained",
  "analogy": "A simple real-world comparison",
  "mapping": [
    {{
      "concept_part": "Part of the original concept",
      "analogy_part": "What it represents in the analogy"
    }}
  ],
  "why_it_helps": "A short explanation of why this analogy makes the concept easier to understand"
}}

Rules:
- Use the source material as the primary source.
- The analogy may use familiar real-world situations.
- Do not change the scientific meaning of the source.
- Do not introduce unsupported scientific facts.
- Keep the analogy appropriate for {class_level["name"]}.
- Use simple language.
- Do not use multiple unrelated analogies.
- Keep the analogy easy to remember.
- Return JSON only.
- Do not use Markdown code fences.
"""

    return prompt.strip()


def clean_json_response(raw_response: str) -> str:
    """
    Remove harmless Markdown formatting from an LLM response
    before JSON parsing.
    """

    response = raw_response.strip()

    # Remove ```json ... ``` or ``` ... ``` fences.
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


def generate_analogy(
    class_id: int,
    source_text: str,
    concept: str,
) -> dict:
    """
    Generate and validate a structured analogy.
    """

    prompt = build_analogy_prompt(
        class_id=class_id,
        source_text=source_text,
        concept=concept,
    )

    raw_response = generate_response(prompt)

    print("\n--- RAW ANALOGY MODEL RESPONSE ---")
    print(repr(raw_response))
    print("--- END RAW ANALOGY MODEL RESPONSE ---\n")

    if not raw_response or not raw_response.strip():
        raise ValueError(
            "The AI model returned an empty analogy response."
        )

    cleaned_response = clean_json_response(raw_response)

    print("--- CLEANED ANALOGY RESPONSE ---")
    print(cleaned_response)
    print("--- END CLEANED ANALOGY RESPONSE ---\n")

    try:
        analogy = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Model returned invalid analogy JSON: {error}"
        ) from error

    required_fields = [
        "concept",
        "analogy",
        "mapping",
        "why_it_helps",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in analogy
    ]

    if missing_fields:
        raise ValueError(
            "Analogy is missing required fields: "
            + ", ".join(missing_fields)
        )

    if not isinstance(analogy["mapping"], list):
        raise ValueError(
            "mapping must be a list."
        )

    for mapping in analogy["mapping"]:
        if not isinstance(mapping, dict):
            raise ValueError(
                "Each mapping must be an object."
            )

        if "concept_part" not in mapping:
            raise ValueError(
                "Each mapping requires concept_part."
            )

        if "analogy_part" not in mapping:
            raise ValueError(
                "Each mapping requires analogy_part."
            )

    return {
        "class_id": class_id,
        "concept": concept,
        "analogy": analogy["analogy"],
        "mapping": analogy["mapping"],
        "why_it_helps": analogy["why_it_helps"],
    }