from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from app import db, bcrypt
from app.models import Student, Classroom, User, FeePayment, AttendanceRecord
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_PASS

routes = Blueprint("routes", __name__)

# HOME 
@routes.route("/")
def home():
    return jsonify({"message": "Welcome to the School Fees & Attendance Management System!"})

#  AUTH ROUTES 
@routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
        return jsonify({"error": "User already exists"}), 409

    new_user = User(
        username=data["username"],
        email=data["email"],
        role=data["role"]
    )
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

@routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "username": user.username,
                "role": user.role
            },
            expires_delta=timedelta(hours=1)
        )
        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# STUDENT ROUTES 
@routes.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    students = Student.query.all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "guardian_name": s.guardian_name,
            "guardian_contact": s.guardian_contact,
            "classroom": {
                "id": s.classroom.id,
                "name": s.classroom.name
            }
        } for s in students
    ])

@routes.route("/students", methods=["POST"])
@jwt_required()
def create_student():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    data = request.get_json()
    username = data["name"].lower().replace(" ", "_")
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    password_hash = bcrypt.generate_password_hash("student123").decode("utf-8")
    new_user = User(
        username=username,
        email=f"{username}@school.com",
        password=password_hash,
        role="student"
    )
    db.session.add(new_user)
    db.session.flush()

    new_student = Student(
        name=data["name"],
        guardian_name=data["guardian_name"],
        guardian_contact=data["guardian_contact"],
        classroom_id=data["classroom_id"],
        user_id=new_user.id
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        "message": "Student and user account created",
        "student_id": new_student.id,
        "login_username": username,
        "default_password": "student123"
    }), 201

@routes.route("/students/<int:id>", methods=["PATCH"])
@jwt_required()
def update_student(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    student = Student.query.get_or_404(id)
    data = request.get_json()
    student.name = data.get("name", student.name)
    student.guardian_name = data.get("guardian_name", student.guardian_name)
    student.guardian_contact = data.get("guardian_contact", student.guardian_contact)
    student.classroom_id = data.get("classroom_id", student.classroom_id)
    db.session.commit()
    return jsonify({"message": "Student updated"})

@routes.route("/students/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_student(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"})

#  CLASSROOM ROUTES 
@routes.route("/classrooms", methods=["GET"])
@jwt_required()
def get_classrooms():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    classrooms = Classroom.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "student_count": len(c.students)
        } for c in classrooms
    ])

@routes.route("/classrooms", methods=["POST"])
@jwt_required()
def create_classroom():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    data = request.get_json()
    if "name" not in data or not data["name"].strip():
        return jsonify({"error": "Classroom name is required"}), 400

    new_classroom = Classroom(name=data["name"])
    db.session.add(new_classroom)
    db.session.commit()
    return jsonify({"message": "Classroom created", "classroom_id": new_classroom.id}), 201

#  ATTENDANCE ROUTES 
@routes.route("/attendance/<int:id>", methods=["PATCH"])
@jwt_required()
def update_attendance(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    attendance = AttendanceRecord.query.get_or_404(id)
    data = request.get_json()
    attendance.status = data.get("status", attendance.status)
    attendance.date = datetime.strptime(data.get("date"), "%Y-%m-%d") if data.get("date") else attendance.date
    db.session.commit()
    return jsonify({"message": "Attendance updated"})

# FEE ROUTES 
@routes.route("/fees/<int:id>", methods=["PATCH"])
@jwt_required()
def update_fee(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    fee = FeePayment.query.get_or_404(id)
    data = request.get_json()
    fee.amount = data.get("amount", fee.amount)
    fee.term = data.get("term", fee.term)
    fee.payment_date = datetime.strptime(data.get("payment_date"), "%Y-%m-%d") if data.get("payment_date") else fee.payment_date
    db.session.commit()
    return jsonify({"message": "Fee payment updated"})

@routes.route("/fees/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_fee(id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

    fee = FeePayment.query.get_or_404(id)
    db.session.delete(fee)
    db.session.commit()
    return jsonify({"message": "Fee payment deleted"})

# INIT ROUTES 
def init_routes(app):
    app.register_blueprint(routes)
    JWTManager(app)
