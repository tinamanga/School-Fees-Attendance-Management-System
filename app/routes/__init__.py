from flask import Blueprint, jsonify, request
from app import db, bcrypt
from app.models import Student, Classroom, User, FeePayment, AttendanceRecord
from datetime import datetime, date


routes = Blueprint("routes", __name__)


# ---------- HOME ----------
@routes.route("/")
def home():
    return jsonify({"message": "Welcome to the School Fees & Attendance Management System!"})


# ---------- AUTH ROUTES ----------
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
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })
    return jsonify({"error": "Invalid username or password"}), 401


# ---------- STUDENT ROUTES ----------
@routes.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "guardian_name": s.guardian_name,
            "guardian_contact": s.guardian_contact,
            "classroom": {
                "id": s.classroom.id,
                "name": s.classroom.name
            }
        })
    return jsonify(result)


@routes.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        "id": student.id,
        "name": student.name,
        "guardian_name": student.guardian_name,
        "guardian_contact": student.guardian_contact,
        "classroom": {
            "id": student.classroom.id,
            "name": student.classroom.name
        },
        "fee_payments": [
            {
                "id": f.id,
                "amount": f.amount,
                "payment_date": f.payment_date.isoformat(),
                "term": f.term
            } for f in student.fee_payments
        ],
        "attendance_records": [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "status": a.status,
                "teacher": {
                    "id": a.teacher.id,
                    "username": a.teacher.username
                }
            } for a in student.attendance_records
        ]
    })

@routes.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()

    username = data["name"].lower().replace(" ", "_")
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    password_hash = bcrypt.generate_password_hash("student123").decode("utf-8")

    new_user = User(
        username=username,
        email=f"{username}@school.com",
        password=password_hash,
        role="student"
    )
    db.session.add(new_user)
    db.session.flush()  # Now new_user.id is available

    new_student = Student(
        name=data["name"],
        guardian_name=data["guardian_name"],
        guardian_contact=data["guardian_contact"],
        classroom_id=data["classroom_id"],
        user_id=new_user.id  # ✅ user_id is now set correctly
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
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()

    student.name = data.get("name", student.name)
    student.guardian_name = data.get("guardian_name", student.guardian_name)
    student.guardian_contact = data.get("guardian_contact", student.guardian_contact)
    student.classroom_id = data.get("classroom_id", student.classroom_id)

    db.session.commit()
    return jsonify({"message": "Student updated"})


@routes.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"})


@routes.route("/students/by-user/<int:user_id>", methods=["GET"])
def get_student_by_user(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "id": student.id,
        "name": student.name,
        "guardian_name": student.guardian_name,
        "guardian_contact": student.guardian_contact,
        "classroom": {
            "id": student.classroom.id,
            "name": student.classroom.name
        },
        "fee_payments": [
            {
                "id": f.id,
                "amount": f.amount,
                "payment_date": f.payment_date.isoformat(),
                "term": f.term
            } for f in student.fee_payments
        ],
        "attendance_records": [
            {
                "id": a.id,
                "date": a.date.isoformat(),
                "status": a.status,
                "teacher": {
                    "id": a.teacher.id,
                    "username": a.teacher.username
                }
            } for a in student.attendance_records
        ]
    })



# ---------- FEE PAYMENT ROUTES ----------
@routes.route("/fee-payments", methods=["POST"])
def add_fee_payment():
    data = request.get_json()

    new_payment = FeePayment(
        student_id=data["student_id"],
        amount=data["amount"],
        term=data["term"]
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({"message": "Payment recorded"}), 201


@routes.route("/fee-payments/student/<int:student_id>", methods=["GET"])
def get_student_payments(student_id):
    payments = FeePayment.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": p.id,
            "amount": p.amount,
            "payment_date": p.payment_date.isoformat(),
            "term": p.term
        } for p in payments
    ])


@routes.route("/fee-payments", methods=["GET"])
def get_all_payments():
    payments = FeePayment.query.all()
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "amount": p.amount,
            "term": p.term,
            "payment_date": p.payment_date.isoformat(),
            "student_id": p.student.id,
            "student_name": p.student.name
        })
    return jsonify(result)


@routes.route("/fee-payments/term/<term>", methods=["GET"])
def get_payments_by_term(term):
    payments = FeePayment.query.filter_by(term=term).all()
    return jsonify([
        {
            "id": p.id,
            "student_id": p.student_id,
            "amount": p.amount,
            "payment_date": p.payment_date.isoformat(),
            "term": p.term
        } for p in payments
    ])


# ---------- ATTENDANCE ROUTES ----------
@routes.route("/attendance/student/<int:student_id>", methods=["GET"])
def get_student_attendance(student_id):
    records = AttendanceRecord.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": r.id,
            "date": r.date.isoformat(),
            "status": r.status,
            "teacher": {
                "id": r.teacher.id,
                "username": r.teacher.username
            }
        } for r in records
    ])


@routes.route("/attendance-records/bulk-weekly", methods=["POST", "OPTIONS"])
def create_bulk_weekly_attendance():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json()
    records = data.get("records", [])
    teacher_id = data.get("teacher_id")

    if not teacher_id or not records:
        return jsonify({"error": "Missing teacher_id or attendance records"}), 400

    try:
        for entry in records:
            student_id = entry["student_id"]
            week = entry["week"]  # dict like {"Mon": "Present", "Tue": "Absent", ...}

            for day_str, status in week.items():
                weekday_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
                if day_str not in weekday_map:
                    continue

                today = datetime.utcnow().date()
                day_date = today
                while day_date.weekday() != weekday_map[day_str]:
                    day_date = day_date.replace(day=day_date.day - 1)

                exists = AttendanceRecord.query.filter_by(
                    student_id=student_id,
                    teacher_id=teacher_id,
                    date=day_date
                ).first()

                if not exists:
                    record = AttendanceRecord(
                        student_id=student_id,
                        teacher_id=teacher_id,
                        date=day_date,
                        status=status
                    )
                    db.session.add(record)

        db.session.commit()
        return jsonify({"message": "Weekly attendance recorded successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ---------- CLASSROOM ROUTES ----------
@routes.route("/classrooms", methods=["GET"])
def get_classrooms():
    classrooms = Classroom.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "student_count": len(c.students)
        } for c in classrooms
    ])


@routes.route("/classrooms", methods=["POST"])
def create_classroom():
    data = request.get_json()
    if "name" not in data or not data["name"].strip():
        return jsonify({"error": "Classroom name is required"}), 400

    new_classroom = Classroom(name=data["name"])
    db.session.add(new_classroom)
    db.session.commit()
    return jsonify({"message": "Classroom created", "classroom_id": new_classroom.id}), 201


@routes.route("/classrooms/<int:id>", methods=["PATCH"])
def update_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    data = request.get_json()

    new_name = data.get("name")
    if new_name:
        classroom.name = new_name
        db.session.commit()
        return jsonify({"message": "Classroom updated"})
    else:
        return jsonify({"error": "New name is required"}), 400


@routes.route("/classrooms/<int:id>", methods=["DELETE"])
def delete_classroom(id):
    classroom = Classroom.query.get_or_404(id)

    if classroom.students:
        return jsonify({"error": "Cannot delete a classroom that has students"}), 400

    db.session.delete(classroom)
    db.session.commit()
    return jsonify({"message": "Classroom deleted"})


# ---------- DASHBOARD ROUTES ----------
@routes.route("/dashboard/admin", methods=["GET"])
def admin_dashboard():
    total_students = Student.query.count()
    total_fees = db.session.query(db.func.sum(FeePayment.amount)).scalar() or 0
    total_attendance = AttendanceRecord.query.count()

    return jsonify({
        "total_students": total_students,
        "total_fees": total_fees,
        "total_attendance_records": total_attendance
    })


@routes.route("/dashboard/teacher/<int:teacher_id>", methods=["GET"])
def teacher_dashboard(teacher_id):
    teacher = User.query.filter_by(id=teacher_id, role="teacher").first()
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    records = AttendanceRecord.query.filter_by(teacher_id=teacher_id).all()
    student_ids = list(set([r.student_id for r in records]))
    students = Student.query.filter(Student.id.in_(student_ids)).all()

    return jsonify({
        "teacher_id": teacher.id,
        "teacher_username": teacher.username,
        "attendance_records_count": len(records),
        "students_marked": [
            {
                "id": s.id,
                "name": s.name,
                "classroom": s.classroom.name
            } for s in students
        ]
    })


# ---------- INIT ----------
def init_routes(app):
    app.register_blueprint(routes)

