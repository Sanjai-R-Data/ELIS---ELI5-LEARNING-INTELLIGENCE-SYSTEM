from backend.learning.mastery import calculate_mastery


class LearnerState:
    """
    Store a learner's mastery information by topic.
    """

    def __init__(self):
        self.topics = {}

    def update_topic(
        self,
        topic: str,
        percentage: float,
    ) -> dict:
        """
        Update mastery information for a topic.
        """

        if not topic.strip():
            raise ValueError(
                "Topic cannot be empty."
            )

        mastery = calculate_mastery(
            percentage
        )

        self.topics[topic] = {
            "percentage": mastery["percentage"],
            "mastery": mastery["level"],
        }

        return self.topics[topic]

    def get_topic(
        self,
        topic: str,
    ) -> dict:
        """
        Return mastery information for a topic.
        """

        if topic not in self.topics:
            raise ValueError(
                f"No learner data found for topic: {topic}"
            )

        return self.topics[topic]

    def get_all_topics(self) -> dict:
        """
        Return mastery information for all topics.
        """

        return self.topics