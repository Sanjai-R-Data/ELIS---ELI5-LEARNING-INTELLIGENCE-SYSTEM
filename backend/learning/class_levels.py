CLASS_LEVELS = [
    {
        "id": 6,
        "name": "Class 6",
    },
    {
        "id": 7,
        "name": "Class 7",
    },
    {
        "id": 8,
        "name": "Class 8",
    },
    {
        "id": 9,
        "name": "Class 9",
    },
    {
        "id": 10,
        "name": "Class 10",
    },
    {
        "id": 11,
        "name": "Class 11",
    },
    {
        "id": 12,
        "name": "Class 12",
    },
]


def get_class_levels() -> list[dict]:
    """
    Return the available class levels.
    """

    return CLASS_LEVELS


def is_valid_class(class_id: int) -> bool:
    """
    Check whether the supplied class ID is supported.
    """

    return any(
        class_level["id"] == class_id
        for class_level in CLASS_LEVELS
    )


def get_class_level(class_id: int) -> dict:
    """
    Return information about a specific class level.

    Raises:
        ValueError: If the class level is not supported.
    """

    for class_level in CLASS_LEVELS:
        if class_level["id"] == class_id:
            return class_level

    raise ValueError(f"Unsupported class level: {class_id}")