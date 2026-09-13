"""
recommender.py
----------------
Maps a student's weak topics to concrete learning resources.

Severity -> difficulty mapping is intentional:
  critical / weak  -> beginner resources first (rebuild the foundation)
  moderate         -> intermediate resources (sharpen, don't re-teach)
"""

DIFFICULTY_BY_SEVERITY = {
    "critical": ["beginner"],
    "weak": ["beginner", "intermediate"],
    "moderate": ["intermediate", "advanced"],
}

MAX_RESOURCES_PER_TOPIC = 3


def recommend_for_weak_areas(weak_areas, resources_by_topic):
    """
    weak_areas: output of weakness_detector.get_weak_areas()
    resources_by_topic: dict[topic_id] -> list of resource dicts, each:
        { "resource_id", "title", "resource_type", "url",
          "difficulty", "est_minutes" }

    Returns a list ready for the frontend:
        {
          "topic_id", "topic_name", "subject_name",
          "classification", "average_percentage",
          "resources": [ ...ranked resource dicts... ]
        }
    """
    recommendations = []

    for area in weak_areas:
        candidates = resources_by_topic.get(area["topic_id"], [])
        preferred_difficulties = DIFFICULTY_BY_SEVERITY.get(area["classification"], ["beginner"])

        ranked = sorted(
            candidates,
            key=lambda r: (
                preferred_difficulties.index(r["difficulty"])
                if r["difficulty"] in preferred_difficulties else 99,
                r["est_minutes"],  # quicker wins first among equals
            ),
        )[:MAX_RESOURCES_PER_TOPIC]

        recommendations.append({
            "topic_id": area["topic_id"],
            "topic_name": area["topic_name"],
            "subject_name": area["subject_name"],
            "classification": area["classification"],
            "average_percentage": area["average_percentage"],
            "resources": ranked,
        })

    return recommendations
