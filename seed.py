from app import create_app
from models import db, User, Classroom, Student, AttendanceRecord, FeePayment
from faker import Faker
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random

fake = Faker()
app = create_app()

with app.app_context():

    AttendanceRecord.query.delete()
    FeePayment.query.delete()
    Student.query.delete()
    Classroom.query.delete()
    User.query.delete()
    print("Cleared all tables")

    admin = User(username="admin", email="admin@example.com", password=generate_password_hash("admin123"), role="admin")
    db.session.add(admin)

    teachers = []
    for i in range(3):
        teacher = User(
            username=f"teacher{i+1}",
            email=f"teacher{i+1}@school.com",
            password=generate_password_hash("teach123"),
            role="teacher"
        )
        teachers.append(teacher)
        db.session.add(teacher)

    db.session.commit()
    print("Seeded admin and 3 teachers")

    classrooms = []
    for label in ["A", "B", "C"]:
        classroom = Classroom(name=f"Class {label}")
        classrooms.append(classroom)
        db.session.add(classroom)

    db.session.commit()
    print(" Seeded 3 classrooms")

    students = []
    for i in range(20):
        student = Student(
            name=fake.name(),
            classroom_id=random.choice(classrooms).id,
            guardian_name=fake.name(),
            guardian_contact=fake.phone_number()
        )
        students.append(student)
        db.session.add(student)

    db.session.commit()
    print(" Seeded 20 students")

    for student in students:
        for j in range(5):
            attendance = AttendanceRecord(
                student_id=student.id,
                teacher_id=random.choice(teachers).id,
                date=date.today() - timedelta(days=j),
                status=random.choice(["Present", "Absent"])
            )
            db.session.add(attendance)

    db.session.commit()
    print("Seeded attendance records")

    for student in students:
        for term in ["Term 1", "Term 2"]:
            fee = FeePayment(
                student_id=student.id,
                amount=random.randint(10000, 20000),
                payment_date=fake.date_between(start_date='-90d', end_date='today'),
                term=term
            )
            db.session.add(fee)

    db.session.commit()
    print("Seeded fee payments")

    print("Database seeding complete.")
