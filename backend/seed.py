from faker import Faker
from app import create_app, db
from app.models import User, Classroom, Student, AttendanceRecord, FeePayment
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

app = create_app()
fake = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create classrooms
    classrooms = []
    for i in range(1, 6):
        classroom = Classroom(name=f"Class {i}A")
        db.session.add(classroom)
        classrooms.append(classroom)

    # Create admin and teacher users with hashed passwords
    admin = User(
        username="admin",
        email="admin@example.com",
        password=generate_password_hash("adminpass"),
        role="admin"
    )
    teacher = User(
        username="teacher",
        email="teacher@example.com",
        password=generate_password_hash("teacherpass"),
        role="teacher"
    )
    db.session.add_all([admin, teacher])

    # Create students
    students = []
    for _ in range(25):
        student = Student(
            name=fake.name(),
            classroom=random.choice(classrooms),
            guardian_name=fake.name(),
            guardian_contact=f"+2547{random.randint(10000000, 99999999)}"
        )
        db.session.add(student)
        students.append(student)

    db.session.commit()  

    # Create attendance records
    for student in students:
        for i in range(5):  # 5 attendance entries per student
            attendance = AttendanceRecord(
                student_id=student.id,
                teacher_id=teacher.id,
                date=date.today() - timedelta(days=i),
                status=random.choice(["Present", "Absent"])
            )
            db.session.add(attendance)

    # Create fee payments
    for student in students:
        for term in ["Term 1", "Term 2", "Term 3"]:
            payment = FeePayment(
                student_id=student.id,
                amount=random.randint(5000, 20000),
                payment_date=fake.date_this_year(),
                term=term
            )
            db.session.add(payment)

    db.session.commit()
    print("Database seeded with Faker data.")
