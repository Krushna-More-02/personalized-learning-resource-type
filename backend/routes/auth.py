from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from backend.models import db
from backend.models.models import Student

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    required = ("full_name", "email", "password", "class_grade")
    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    student = Student(
        full_name=data["full_name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        class_grade=data["class_grade"],
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Account created", "student_id": student.student_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email", "")
    password = data.get("password", "")

    student = Student.query.filter_by(email=email).first()
    if not student or not check_password_hash(student.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["student_id"] = student.student_id
    return jsonify({
        "message": "Logged in",
        "student": {
            "student_id": student.student_id,
            "full_name": student.full_name,
            "class_grade": student.class_grade,
        },
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("student_id", None)
    return jsonify({"message": "Logged out"})
