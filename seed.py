# seed.py

from datetime import date, timedelta
from app import create_app, db, bcrypt
from app.models import User, Classroom, Student, AttendanceRecord, FeePayment

app = create_app()

with app.app_context():
    print("🔄 Initializing database...")
    db.create_all()

    # 1. Create Admin
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@school.com",
            role="admin",
            password=bcrypt.generate_password_hash("admin123").decode("utf-8")
        )
        db.session.add(admin)
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin already exists.")

    # 2. Create Teacher
    teacher = User.query.filter_by(username="teacher1").first()
    if not teacher:
        teacher = User(
            username="teacher1",
            email="teacher1@school.com",
            role="teacher",
            password=bcrypt.generate_password_hash("teacher123").decode("utf-8")
        )
        db.session.add(teacher)
        print("✅ Teacher user created.")
    else:
        print("ℹ️ Teacher already exists.")

    # 3. Create Classroom
    classroom = Classroom.query.filter_by(name="Grade 1").first()
    if not classroom:
        classroom = Classroom(name="Grade 1")
        db.session.add(classroom)
        db.session.flush()
        print("✅ Classroom 'Grade 1' created.")
    else:
        print("ℹ️ Classroom 'Grade 1' already exists.")

    # 4. Create Student and Link to User
    student_user = User.query.filter_by(username="student1").first()
    if not student_user:
        student_user = User(
            username="student1",
            email="student1@school.com",
            role="student",
            password=bcrypt.generate_password_hash("student123").decode("utf-8")
        )
        db.session.add(student_user)
        db.session.flush()

        student = Student(
            name="Student One",
            guardian_name="Guardian A",
            guardian_contact="0712345678",
            classroom_id=classroom.id,
            user_id=student_user.id
        )
        db.session.add(student)
        db.session.flush()
        print("✅ Student user and profile created.")
    else:
        student = Student.query.filter_by(user_id=student_user.id).first()
        if not student:
            student = Student(
                name="Student One",
                guardian_name="Guardian A",
                guardian_contact="0712345678",
                classroom_id=classroom.id,
                user_id=student_user.id
            )
            db.session.add(student)
            db.session.flush()
            print("✅ Student profile created for existing user.")
        else:
            print("ℹ️ Student already exists.")

    # 5. Sample Fee Payments
    if not FeePayment.query.filter_by(student_id=student.id).first():
        sample_payments = [
            FeePayment(student_id=student.id, amount=5000, term="Term 1"),
            FeePayment(student_id=student.id, amount=3000, term="Term 2"),
        ]
        db.session.add_all(sample_payments)
        print("💰 Sample fee payments added.")
    else:
        print("ℹ️ Fee payments already exist for student1.")

    # 6. Sample Attendance Records
    if not AttendanceRecord.query.filter_by(student_id=student.id).first():
        today = date.today()
        week_days = [today - timedelta(days=i) for i in range(5)]  # Last 5 days

        attendance_records = [
            AttendanceRecord(student_id=student.id, teacher_id=teacher.id, date=d, status="Present" if i % 2 == 0 else "Absent")
            for i, d in enumerate(reversed(week_days))
        ]
        db.session.add_all(attendance_records)
        print("📋 Sample attendance records added.")
    else:
        print("ℹ️ Attendance already exists for student1.")

    # ✅ Commit all changes
    db.session.commit()
    print("🎉 Database seeded successfully with users, student, attendance, and fees.")

