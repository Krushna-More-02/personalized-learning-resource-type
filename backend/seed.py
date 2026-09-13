"""
Run once after loading database/schema.sql to set the demo student's
real password hash (schema.sql ships a placeholder since you should
never commit a real hash to source control).

Usage:
    cd personalized-learning-resource
    python -m backend.seed
"""
from werkzeug.security import generate_password_hash
from backend.app import create_app
from backend.models import db
from backend.models.models import Student

app = create_app()

with app.app_context():
    demo = Student.query.filter_by(email="demo@student.com").first()
    if demo:
        demo.password_hash = generate_password_hash("password123")
        db.session.commit()
        print("Demo account ready -> demo@student.com / password123")
    else:
        print("Demo student not found — did you load database/schema.sql first?")
