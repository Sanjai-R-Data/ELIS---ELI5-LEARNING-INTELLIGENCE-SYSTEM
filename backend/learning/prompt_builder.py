from backend.learning.class_levels import get_class_level


def build_explanation_prompt(
    class_id: int,
    source_text: str,
    instruction: str,
) -> str:
    """
    Build a class-aware, source-grounded prompt that asks
    the model to return a structured JSON explanation.
    """

    class_level = get_class_level(class_id)

    if not source_text.strip():
        raise ValueError("Source text cannot be empty.")

    if not instruction.strip():
        raise ValueError("Instruction cannot be empty.")

    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student is learning from the following source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Learning task:
{instruction}

Create an explanation suitable for {class_level["name"]}.

Return ONLY valid JSON.

The JSON must follow exactly this structure:

{{
  "title": "Short title of the topic",
  "simple_explanation": "Clear explanation suitable for the student's class",
  "key_points": [
    "Important point 1",
    "Important point 2",
    "Important point 3"
  ],
  "simple_example": "One simple example or comparison",
  "important_terms": [
    {{
      "term": "Term 1",
      "meaning": "Simple meaning"
    }},
    {{
      "term": "Term 2",
      "meaning": "Simple meaning"
    }}
  ]
}}

Rules:
- Use the provided source material as the primary source.
- Stay grounded in the source material.
- Do not invent unsupported facts.
- Do not introduce unrelated topics.
- Do not simply copy the source.
- Match the vocabulary and depth to {class_level["name"]}.
- Use short and clear sentences.
- Include 3 to 5 key points.
- Include up to 5 important terms.
- Return JSON only.
- Do not use Markdown code fences.
"""

    return prompt.strip()