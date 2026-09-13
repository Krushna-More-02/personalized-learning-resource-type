from datetime import datetime
from backend.models import db


class Student(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    class_grade = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subject(db.Model):
    __tablename__ = "subjects"
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), unique=True, nullable=False)


class Topic(db.Model):
    __tablename__ = "topics"
    topic_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.subject_id"))
    topic_name = db.Column(db.String(150), nullable=False)
    topic_weight = db.Column(db.Numeric(3, 2), default=1.0)

    subject = db.relationship("Subject")


class Exam(db.Model):
    __tablename__ = "exams"
    exam_id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(150), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.subject_id"))
    exam_date = db.Column(db.Date, nullable=False)


class Mark(db.Model):
    __tablename__ = "marks"
    mark_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"))
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"))
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.exam_id"))
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=False)
    max_marks = db.Column(db.Numeric(5, 2), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    topic = db.relationship("Topic")
    exam = db.relationship("Exam")


class Resource(db.Model):
    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"))
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.Enum("video", "article", "pdf", "practice_set", "course"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    difficulty = db.Column(db.Enum("beginner", "intermediate", "advanced"), nullable=False)
    est_minutes = db.Column(db.Integer, default=15)


class Recommendation(db.Model):
    __tablename__ = "recommendations"
    recommendation_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"))
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"))
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.resource_id"))
    severity = db.Column(db.Enum("critical", "weak", "moderate"), nullable=False)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum("pending", "in_progress", "completed"), default="pending")
