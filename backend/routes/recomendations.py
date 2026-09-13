from flask import Blueprint, jsonify
from backend.models import db
from backend.models.models import Mark, Topic, Subject, Exam, Resource
from recommendation.weakness_detector import analyze_student_marks, get_weak_areas
from recommendation.recommender import recommend_for_weak_areas

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api")


def _fetch_marks_rows(student_id):
    rows = (
        db.session.query(Mark, Topic, Subject, Exam)
        .join(Topic, Mark.topic_id == Topic.topic_id)
        .join(Subject, Topic.subject_id == Subject.subject_id)
        .join(Exam, Mark.exam_id == Exam.exam_id)
        .filter(Mark.student_id == student_id)
        .all()
    )
    return [
        {
            "topic_id": topic.topic_id,
            "topic_name": topic.topic_name,
            "subject_name": subject.subject_name,
            "marks_obtained": float(mark.marks_obtained),
            "max_marks": float(mark.max_marks),
            "exam_date": exam.exam_date.isoformat(),
        }
        for mark, topic, subject, exam in rows
    ]


@recommendations_bp.route("/students/<int:student_id>/weaknesses", methods=["GET"])
def weaknesses(student_id):
    marks_rows = _fetch_marks_rows(student_id)
    if not marks_rows:
        return jsonify({"topics": [], "message": "No marks recorded yet"})
    return jsonify({"topics": analyze_student_marks(marks_rows)})


@recommendations_bp.route("/students/<int:student_id>/recommendations", methods=["GET"])
def recommendations(student_id):
    marks_rows = _fetch_marks_rows(student_id)
    if not marks_rows:
        return jsonify({"recommendations": [], "message": "No marks recorded yet"})

    weak_areas = get_weak_areas(marks_rows)
    topic_ids = [w["topic_id"] for w in weak_areas]

    resources_by_topic = {}
    if topic_ids:
        resource_rows = Resource.query.filter(Resource.topic_id.in_(topic_ids)).all()
        for r in resource_rows:
            resources_by_topic.setdefault(r.topic_id, []).append({
                "resource_id": r.resource_id,
                "title": r.title,
                "resource_type": r.resource_type,
                "url": r.url,
                "difficulty": r.difficulty,
                "est_minutes": r.est_minutes,
            })

    recs = recommend_for_weak_areas(weak_areas, resources_by_topic)
    return jsonify({"recommendations": recs})
