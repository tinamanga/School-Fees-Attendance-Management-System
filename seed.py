from app import app
from models import db, User, Classroom, Student, AttendanceRecord, FeePayment
from faker import Faker
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random

fake = Faker()

with app.app_context():

   
    AttendanceRecord.query.delete()
    FeePayment.query.delete()
    Student.query.delete()
    Classroom.query.delete()
    User.query.delete()
    db.session.commit()
    print("Cleared all tables")

    # Seed one admin
    admin = User(
        username="admin",
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add(admin)

    # Seed 10 teachers
    teachers = []
    for i in range(10):
        teacher = User(
            username=f"teacher{i+1}",
            email=f"teacher{i+1}@school.com",
            password=generate_password_hash("teach123"),
            role="teacher"
        )
        db.session.add(teacher)
        teachers.append(teacher)

    db.session.commit()
    print(" Seeded 1 admin and 10 teachers")

    # Seed 3 classrooms
    classrooms = []
    for label in ["A", "B", "C"]:
        classroom = Classroom(name=f"Class {label}")
        db.session.add(classroom)
        classrooms.append(classroom)

    db.session.commit()
    print("Seeded 3 classrooms")

    # Seed 40 students
    students = []
    for _ in range(40):
        student = Student(
            name=fake.name(),
            classroom_id=random.choice(classrooms).id,
            guardian_name=fake.name(),
            guardian_contact=fake.phone_number()
        )
        db.session.add(student)
        students.append(student)

    db.session.commit()
    print(" Seeded 40 students")

    # Seed attendance records for each student
    for student in students:
        for j in range(20):  # last 20 days
            attendance = AttendanceRecord(
                student_id=student.id,
                teacher_id=random.choice(teachers).id,
                date=date.today() - timedelta(days=j),
                status=random.choice(["Present", "Absent"])
            )
            db.session.add(attendance)

    db.session.commit()
    print("Seeded attendance records")

    # Add parents
    parents = []
    for i in range(5):
        parent = User(
            username=f"parent{i+1}",
            email=f"parent{i+1}@school.com",
            password=generate_password_hash("parent123"),
            role="parent"
        )
        parents.append(parent)
        db.session.add(parent)

    db.session.commit()
    print("Seeded 5 parents")


    # Seed fee payments for each student
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
