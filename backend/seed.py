from app import create_app, db
from app.models import User, Student, Classroom, AttendanceRecord, FeePayment

app = create_app()

with app.app_context():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # Create Classrooms
    c1 = Classroom(name="Grade 6")
    c2 = Classroom(name="Grade 7")
    db.session.add_all([c1, c2])
    db.session.commit()

    # Create Students
    s1 = Student(name="Brian", classroom_id=c1.id, guardian_name="Mr. Otieno", guardian_contact="0712345678")
    s2 = Student(name="Amina", classroom_id=c2.id, guardian_name="Mrs. Amina", guardian_contact="0711223344")
    db.session.add_all([s1, s2])
    db.session.commit()

    # Create Users (teachers)
    t1 = User(username="teacher_jane", email="jane@school.com", password="pass123", role="teacher")
    db.session.add(t1)
    db.session.commit()

    # Create Attendance Records
    a1 = AttendanceRecord(student_id=s1.id, teacher_id=t1.id, status="Present")
    a2 = AttendanceRecord(student_id=s2.id, teacher_id=t1.id, status="Absent")
    db.session.add_all([a1, a2])
    db.session.commit()

    # Create Fee Payments
    f1 = FeePayment(student_id=s1.id, amount=5000, term="Term 1")
    f2 = FeePayment(student_id=s2.id, amount=4500, term="Term 1")
    db.session.add_all([f1, f2])
    db.session.commit()

    print("✅ Seed data inserted successfully.")
