"""
weakness_detector.py
---------------------
Rule-based engine that turns raw topic-level marks into a
weakness classification per topic for a given student.

Kept independent of Flask/SQLAlchemy on purpose: it accepts plain
dicts/lists so it can be unit-tested or swapped for an ML model later
without touching the backend routes.
"""

from statistics import mean

# Thresholds (percentage) — tune these as you gather more real data
WEAK_THRESHOLD = 50
IMPROVEMENT_THRESHOLD = 70
STRONG_THRESHOLD = 85

SEVERITY_ORDER = {"critical": 3, "weak": 2, "moderate": 1, "none": 0}


def _percentage(obtained, max_marks):
    return round((obtained / max_marks) * 100, 2) if max_marks else 0


def classify_topic(percentage, trend=None):
    """
    Returns one of: 'critical', 'weak', 'moderate', 'good', 'strong'

    trend: optional float, positive = improving, negative = declining,
    used to bump a borderline topic into a more urgent bucket.
    """
    if percentage < WEAK_THRESHOLD:
        if trend is not None and trend < 0:
            return "critical"          # weak AND getting worse
        return "weak"
    elif percentage < IMPROVEMENT_THRESHOLD:
        return "moderate"
    elif percentage < STRONG_THRESHOLD:
        return "good"
    return "strong"


def analyze_student_marks(marks_rows):
    """
    marks_rows: list of dicts, each like:
        {
          "topic_id": 1,
          "topic_name": "Quadratic Equations",
          "subject_name": "Mathematics",
          "marks_obtained": 12,
          "max_marks": 25,
          "exam_date": "2026-07-10"
        }

    Returns a list of per-topic summaries, sorted worst-first:
        {
          "topic_id", "topic_name", "subject_name",
          "average_percentage", "attempts", "trend",
          "classification"
        }
    """
    by_topic = {}
    for row in marks_rows:
        by_topic.setdefault(row["topic_id"], []).append(row)

    results = []
    for topic_id, rows in by_topic.items():
        rows_sorted = sorted(rows, key=lambda r: r["exam_date"])
        percentages = [_percentage(r["marks_obtained"], r["max_marks"]) for r in rows_sorted]
        avg_pct = round(mean(percentages), 2)

        trend = None
        if len(percentages) >= 2:
            # simple trend: last attempt vs average of everything before it
            trend = round(percentages[-1] - mean(percentages[:-1]), 2)

        classification = classify_topic(avg_pct, trend)

        results.append({
            "topic_id": topic_id,
            "topic_name": rows_sorted[0]["topic_name"],
            "subject_name": rows_sorted[0]["subject_name"],
            "average_percentage": avg_pct,
            "attempts": len(rows_sorted),
            "trend": trend,
            "classification": classification,
        })

    # Worst areas first: critical > weak > moderate > good > strong
    results.sort(key=lambda r: (
        -SEVERITY_ORDER.get(r["classification"], 0),
        r["average_percentage"]
    ))
    return results


def get_weak_areas(marks_rows):
    """Convenience filter: only topics that actually need attention."""
    analyzed = analyze_student_marks(marks_rows)
    return [r for r in analyzed if r["classification"] in ("critical", "weak", "moderate")]
