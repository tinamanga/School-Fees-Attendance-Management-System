from flask import Blueprint, jsonify, request
from app.models import db, User, Student, Classroom, AttendanceRecord, FeePayment
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

main = Blueprint('main', __name__)

# -------------------------------
# GET current user info
# -------------------------------
@main.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200

# -------------------------------
# GET all classrooms
# -------------------------------
@main.route('/classrooms', methods=['GET'])
@jwt_required()
def get_classrooms():
    classrooms = Classroom.query.all()
    result = [{"id": c.id, "name": c.name} for c in classrooms]
    return jsonify(result), 200

# -------------------------------
# GET a single classroom by ID
# -------------------------------
@main.route('/classrooms/<int:id>', methods=['GET'])
@jwt_required()
def get_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    return jsonify({"id": classroom.id, "name": classroom.name}), 200

# -------------------------------
# GET all students
# -------------------------------
@main.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    result = []
    for student in students:
        result.append({
            "id": student.id,
            "name": student.name,
            "classroom": student.classroom.name if student.classroom else None,
            "guardian_name": student.guardian_name,
            "guardian_contact": student.guardian_contact
        })
    return jsonify(result), 200

# -------------------------------
# GET single student by ID
# -------------------------------
@main.route('/students/<int:id>', methods=['GET'])
@jwt_required()
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        "id": student.id,
        "name": student.name,
        "classroom": student.classroom.name if student.classroom else None,
        "guardian_name": student.guardian_name,
        "guardian_contact": student.guardian_contact
    }), 200

# -------------------------------
# POST attendance record
# -------------------------------
@main.route('/attendance', methods=['POST'])
@jwt_required()
def post_attendance():
    data = request.json

    required_fields = ['student_id', 'teacher_id', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required"}), 400

    try:
        record = AttendanceRecord(
            student_id=data['student_id'],
            teacher_id=data['teacher_id'],
            date=date.today(),
            status=data['status']
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Attendance recorded"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------------------
# POST fee payment
# -------------------------------
@main.route('/fee-payments', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.json
    payment = FeePayment(
        student_id=data['student_id'],
        amount=data['amount'],
        payment_date=date.today(),
        term=data['term']
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"message": "Fee payment recorded"}), 201

# -------------------------------
# GET payments for a student
# -------------------------------
@main.route('/fee-payments/<int:student_id>', methods=['GET'])
@jwt_required()
def get_payments(student_id):
    payments = FeePayment.query.filter_by(student_id=student_id).all()
    result = []
    for pay in payments:
        result.append({
            "amount": pay.amount,
            "payment_date": pay.payment_date.strftime('%Y-%m-%d'),
            "term": pay.term
        })
    return jsonify(result), 200

# -------------------------------
# POST login (with JWT)
# -------------------------------
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user_id": user.id,
            "role": user.role
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

# -------------------------------
# POST register (Admin only)
# -------------------------------
@main.route('/register', methods=['POST'])
@jwt_required()
def register():
    identity = get_jwt_identity()
    requesting_user = User.query.get(identity['id'])

    if requesting_user.role != 'admin':
        return jsonify({"error": "Unauthorized. Only admin can register users."}), 403

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'teacher')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# -------------------------------
# POST logout (stateless client)
# -------------------------------
@main.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful. Please discard token on client side."}), 200


# -------------------------------
# CREATE a classroom (Admin only)
# -------------------------------
@main.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])

    if user.role != 'admin':
        return jsonify({"error": "Only admins can create classrooms"}), 403

    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Classroom name is required"}), 400

    classroom = Classroom(name=name)
    db.session.add(classroom)
    db.session.commit()
    return jsonify({"message": "Classroom created", "id": classroom.id}), 201

# -------------------------------
# UPDATE a classroom (Admin only)
# -------------------------------
@main.route('/classrooms/<int:id>', methods=['PUT'])
@jwt_required()
def update_classroom(id):
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])

    if user.role != 'admin':
        return jsonify({"error": "Only admins can update classrooms"}), 403

    classroom = Classroom.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Classroom name is required"}), 400

    classroom.name = name
    db.session.commit()
    return jsonify({"message": "Classroom updated"}), 200

# -------------------------------
# DELETE a classroom (Admin only)
# -------------------------------
@main.route('/classrooms/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_classroom(id):
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])

    if user.role != 'admin':
        return jsonify({"error": "Only admins can delete classrooms"}), 403

    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return jsonify({"message": "Classroom deleted"}), 200
