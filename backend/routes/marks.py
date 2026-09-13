from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.models import Mark, Topic, Subject, Exam

marks_bp = Blueprint("marks", __name__, url_prefix="/api/marks")


@marks_bp.route("/<int:student_id>", methods=["GET"])
def get_marks(student_id):
    """All topic-level marks for a student, joined with topic/subject names."""
    rows = (
        db.session.query(Mark, Topic, Subject, Exam)
        .join(Topic, Mark.topic_id == Topic.topic_id)
        .join(Subject, Topic.subject_id == Subject.subject_id)
        .join(Exam, Mark.exam_id == Exam.exam_id)
        .filter(Mark.student_id == student_id)
        .all()
    )

    result = [
        {
            "topic_id": topic.topic_id,
            "topic_name": topic.topic_name,
            "subject_name": subject.subject_name,
            "marks_obtained": float(mark.marks_obtained),
            "max_marks": float(mark.max_marks),
            "exam_name": exam.exam_name,
            "exam_date": exam.exam_date.isoformat(),
        }
        for mark, topic, subject, exam in rows
    ]
    return jsonify(result)


@marks_bp.route("", methods=["POST"])
def add_mark():
    """Teacher/admin endpoint to record a new topic-level score."""
    data = request.get_json(force=True)
    required = ("student_id", "topic_id", "exam_id", "marks_obtained", "max_marks")
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    mark = Mark(
        student_id=data["student_id"],
        topic_id=data["topic_id"],
        exam_id=data["exam_id"],
        marks_obtained=data["marks_obtained"],
        max_marks=data["max_marks"],
    )
    db.session.add(mark)
    db.session.commit()
    return jsonify({"message": "Mark recorded", "mark_id": mark.mark_id}), 201
