import json
import re

from backend.learning.class_levels import get_class_level
from backend.llm.ollama_client import generate_response

MAX_TOPICS = 8

def build_topic_prompt(
    class_id: int,
    source_text: str,
) -> str:
    """
    Build a class-aware prompt for extracting
    learning topics from textbook source material.
    """

    class_level = get_class_level(
        class_id
    )


    if not source_text.strip():

        raise ValueError(
            "Source text cannot be empty."
        )


    prompt = f"""
You are ELIS, an educational AI tutor.

Student level:
{class_level["name"]}

The student is learning from the following
textbook source material:

--- SOURCE MATERIAL ---
{source_text}
--- END SOURCE MATERIAL ---

Your task is to identify the main learnable
topics that are explicitly present in the
provided textbook material.

A topic should represent a meaningful concept,
chapter idea, process, principle, or subject
that a student could learn from this material.

IMPORTANT RULES:

- Use ONLY information supported by the source.
- Do not invent topics that are not present.
- Do not use outside knowledge.
- Do not create overly broad topics such as
  "Science" or "Biology" unless the source
  explicitly focuses on that as a topic.
- Do not create tiny fragments such as
  individual sentences.
- Combine closely related fragments into one
  meaningful learning topic.
- Use simple topic titles appropriate for the
  student's level.
- Provide a short description for each topic.
- Return the most important topics first.
- Return at most {MAX_TOPICS} topics.
- If the source contains fewer meaningful topics,
  return fewer topics.

Return ONLY valid JSON using exactly this format:

{{
    "topics": [
        {{
            "id": "topic_1",
            "title": "Topic title",
            "description": "Short simple description"
        }},
        {{
            "id": "topic_2",
            "title": "Topic title",
            "description": "Short simple description"
        }}
    ]
}}

Do not use Markdown.
Do not use code fences.
Return JSON only.
"""

    return prompt.strip()


def clean_json_response(
    raw_response: str,
) -> str:
    """
    Remove Markdown code fences and surrounding
    whitespace from an LLM JSON response.
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

def validate_topic(
    topic: dict,
    index: int,
) -> dict:
    """
    Validate and normalize a single topic.
    """

    if not isinstance(
        topic,
        dict,
    ):

        raise ValueError(
            f"Topic {index} must be an object."
        )


    title = topic.get(
        "title"
    )


    description = topic.get(
        "description"
    )


    if not isinstance(
        title,
        str,
    ) or not title.strip():

        raise ValueError(
            f"Topic {index} is missing a valid title."
        )


    if not isinstance(
        description,
        str,
    ) or not description.strip():

        raise ValueError(
            f"Topic {index} is missing a valid description."
        )


    return {

        "id":
            f"topic_{index}",

        "title":
            title.strip(),

        "description":
            description.strip(),

    }

def extract_topics(
    class_id: int,
    source_text: str,
) -> list[dict]:
    """
    Extract and validate learning topics from
    textbook source material.
    """

    prompt = build_topic_prompt(
        class_id=class_id,
        source_text=source_text,
    )


    raw_response = generate_response(
        prompt
    )


    if (
        not raw_response
        or not raw_response.strip()
    ):

        raise ValueError(
            "The AI model returned an empty topic list."
        )


    cleaned_response = clean_json_response(
        raw_response
    )


    try:

        result = json.loads(
            cleaned_response
        )


    except json.JSONDecodeError as error:

        print(
            "\n--- RAW TOPIC MODEL RESPONSE ---"
        )

        print(
            repr(raw_response)
        )

        print(
            "\n--- CLEANED TOPIC JSON ---"
        )

        print(
            cleaned_response
        )

        print(
            "\n--- END TOPIC DEBUG ---"
        )


        raise ValueError(
            f"Model returned invalid topic JSON: {error}"
        ) from error


    if not isinstance(
        result,
        dict,
    ):

        raise ValueError(
            "Topic response must be a JSON object."
        )


    topics = result.get(
        "topics"
    )


    if not isinstance(
        topics,
        list,
    ):

        raise ValueError(
            "Topic response must contain a topics list."
        )


    if not topics:

        raise ValueError(
            "No learning topics were found in the source."
        )


    validated_topics = []


    for index, topic in enumerate(
        topics[:MAX_TOPICS],
        start=1,
    ):

        validated_topic = validate_topic(
            topic=topic,
            index=index,
        )


        validated_topics.append(
            validated_topic
        )


    if not validated_topics:

        raise ValueError(
            "No valid learning topics were produced."
        )


    return validated_topics