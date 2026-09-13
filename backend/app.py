"""
Pathwise — Personalized Learning Resource System
Single-file Flask backend: models + routes + recommendation logic.
"""
from datetime import datetime
from statistics import mean

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---------------------------------------------------------------
# CONFIG — change these to match your MySQL setup
# ---------------------------------------------------------------
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_DB = os.environ.get("MYSQL_DB", "learning_resource_db")

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-change-this"
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)

# ---------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------
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


class Resource(db.Model):
    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.topic_id"))
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(30), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    est_minutes = db.Column(db.Integer, default=15)


# ---------------------------------------------------------------
# RECOMMENDATION LOGIC (rule-based)
# ---------------------------------------------------------------
WEAK_THRESHOLD = 50
IMPROVEMENT_THRESHOLD = 70
STRONG_THRESHOLD = 85
SEVERITY_ORDER = {"critical": 3, "weak": 2, "moderate": 1, "good": 0, "strong": -1}
DIFFICULTY_BY_SEVERITY = {
    "critical": ["beginner"],
    "weak": ["beginner", "intermediate"],
    "moderate": ["intermediate", "advanced"],
}


def classify_topic(percentage, trend=None):
    if percentage < WEAK_THRESHOLD:
        return "critical" if (trend is not None and trend < 0) else "weak"
    elif percentage < IMPROVEMENT_THRESHOLD:
        return "moderate"
    elif percentage < STRONG_THRESHOLD:
        return "good"
    return "strong"


def analyze_marks(marks_rows):
    by_topic = {}
    for row in marks_rows:
        by_topic.setdefault(row["topic_id"], []).append(row)

    results = []
    for topic_id, rows in by_topic.items():
        rows_sorted = sorted(rows, key=lambda r: r["exam_date"])
        percentages = [round((r["marks_obtained"] / r["max_marks"]) * 100, 2) for r in rows_sorted]
        avg_pct = round(mean(percentages), 2)

        trend = None
        if len(percentages) >= 2:
            trend = round(percentages[-1] - mean(percentages[:-1]), 2)

        results.append({
            "topic_id": topic_id,
            "topic_name": rows_sorted[0]["topic_name"],
            "subject_name": rows_sorted[0]["subject_name"],
            "average_percentage": avg_pct,
            "attempts": len(rows_sorted),
            "trend": trend,
            "classification": classify_topic(avg_pct, trend),
        })

    results.sort(key=lambda r: (-SEVERITY_ORDER[r["classification"]], r["average_percentage"]))
    return results


def recommend_resources(weak_areas, resources_by_topic):
    recs = []
    for area in weak_areas:
        candidates = resources_by_topic.get(area["topic_id"], [])
        preferred = DIFFICULTY_BY_SEVERITY.get(area["classification"], ["beginner"])
        ranked = sorted(
            candidates,
            key=lambda r: (preferred.index(r["difficulty"]) if r["difficulty"] in preferred else 99, r["est_minutes"]),
        )[:3]
        recs.append({**area, "resources": ranked})
    return recs


def fetch_marks_rows(student_id):
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
            "topic_id": t.topic_id, "topic_name": t.topic_name, "subject_name": s.subject_name,
            "marks_obtained": float(m.marks_obtained), "max_marks": float(m.max_marks),
            "exam_date": e.exam_date.isoformat(),
        }
        for m, t, s, e in rows
    ]


# ---------------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    if not all(data.get(k) for k in ("full_name", "email", "password", "class_grade")):
        return jsonify({"error": "Missing required fields"}), 400
    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "An account with this email already exists"}), 409
    student = Student(
        full_name=data["full_name"], email=data["email"],
        password_hash=generate_password_hash(data["password"]), class_grade=data["class_grade"],
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Account created", "student_id": student.student_id}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    student = Student.query.filter_by(email=data.get("email", "")).first()
    if not student or not check_password_hash(student.password_hash, data.get("password", "")):
        return jsonify({"error": "Invalid email or password"}), 401
    session["student_id"] = student.student_id
    return jsonify({"student": {
        "student_id": student.student_id, "full_name": student.full_name, "class_grade": student.class_grade,
    }})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("student_id", None)
    return jsonify({"message": "Logged out"})


# ---------------------------------------------------------------
# LOOKUP ROUTES (used by the Add Marks admin page)
# ---------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
def list_students():
    students = Student.query.order_by(Student.full_name).all()
    return jsonify([
        {"student_id": s.student_id, "full_name": s.full_name, "class_grade": s.class_grade}
        for s in students
    ])


@app.route("/api/subjects", methods=["GET"])
def list_subjects():
    subjects = Subject.query.order_by(Subject.subject_name).all()
    return jsonify([{"subject_id": s.subject_id, "subject_name": s.subject_name} for s in subjects])


@app.route("/api/topics", methods=["GET"])
def list_topics():
    rows = db.session.query(Topic, Subject).join(Subject, Topic.subject_id == Subject.subject_id).order_by(Subject.subject_name, Topic.topic_name).all()
    return jsonify([
        {"topic_id": t.topic_id, "topic_name": t.topic_name, "subject_name": s.subject_name, "subject_id": s.subject_id}
        for t, s in rows
    ])


@app.route("/api/exams", methods=["GET"])
def list_exams():
    rows = db.session.query(Exam, Subject).join(Subject, Exam.subject_id == Subject.subject_id).order_by(Exam.exam_date.desc()).all()
    return jsonify([
        {"exam_id": e.exam_id, "exam_name": e.exam_name, "subject_name": s.subject_name,
         "subject_id": s.subject_id, "exam_date": e.exam_date.isoformat()}
        for e, s in rows
    ])


@app.route("/api/exams", methods=["POST"])
def create_exam():
    data = request.get_json(force=True)
    if not all(data.get(k) for k in ("exam_name", "subject_id", "exam_date")):
        return jsonify({"error": "Missing required fields"}), 400
    exam = Exam(exam_name=data["exam_name"], subject_id=data["subject_id"], exam_date=data["exam_date"])
    db.session.add(exam)
    db.session.commit()
    return jsonify({"message": "Exam created", "exam_id": exam.exam_id}), 201


# ---------------------------------------------------------------
# MARKS
# ---------------------------------------------------------------
@app.route("/api/marks", methods=["POST"])
def add_mark():
    """Used by the Add Marks admin page — records one topic-level score."""
    data = request.get_json(force=True)
    required = ("student_id", "topic_id", "exam_id", "marks_obtained", "max_marks")
    if not all(data.get(k) not in (None, "") for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    mark = Mark(
        student_id=data["student_id"], topic_id=data["topic_id"], exam_id=data["exam_id"],
        marks_obtained=data["marks_obtained"], max_marks=data["max_marks"],
    )
    db.session.add(mark)
    db.session.commit()
    return jsonify({"message": "Mark recorded", "mark_id": mark.mark_id}), 201


# ---------------------------------------------------------------
# RECOMMENDATION ROUTES
# ---------------------------------------------------------------
@app.route("/api/students/<int:student_id>/weaknesses", methods=["GET"])
def weaknesses(student_id):
    rows = fetch_marks_rows(student_id)
    if not rows:
        return jsonify({"topics": []})
    return jsonify({"topics": analyze_marks(rows)})


@app.route("/api/students/<int:student_id>/recommendations", methods=["GET"])
def recommendations(student_id):
    rows = fetch_marks_rows(student_id)
    if not rows:
        return jsonify({"recommendations": []})

    analyzed = analyze_marks(rows)
    weak_areas = [a for a in analyzed if a["classification"] in ("critical", "weak", "moderate")]

    topic_ids = [w["topic_id"] for w in weak_areas]
    resources_by_topic = {}
    if topic_ids:
        for r in Resource.query.filter(Resource.topic_id.in_(topic_ids)).all():
            resources_by_topic.setdefault(r.topic_id, []).append({
                "resource_id": r.resource_id, "title": r.title, "resource_type": r.resource_type,
                "url": r.url, "difficulty": r.difficulty, "est_minutes": r.est_minutes,
            })

    return jsonify({"recommendations": recommend_resources(weak_areas, resources_by_topic)})


# ---------------------------------------------------------------
# SERVE FRONTEND
# ---------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# ---------------------------------------------------------------
# ONE-TIME SETUP: run  python backend/app.py setseed  to fix the demo password
# ---------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setseed":
        with app.app_context():
            demo = Student.query.filter_by(email="demo@student.com").first()
            if demo:
                demo.password_hash = generate_password_hash("password123")
                db.session.commit()
                print("Demo account ready -> demo@student.com / password123")
            else:
                print("Demo student not found — did you run schema.sql first?")
    else:
        app.run(debug=True, port=5000)