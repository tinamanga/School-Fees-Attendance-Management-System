from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', etc.
    subject = db.Column(db.String(100))

    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))  # ✅ FIXED
    classroom = relationship('Classroom', backref='teachers')

    # If user is a teacher, they can have multiple attendance records
    attendance_records = relationship('AttendanceRecord', backref='teacher', lazy=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"



class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    students = relationship('Student', back_populates='classroom', lazy=True)

    def __repr__(self):
        return f"<Classroom {self.name}>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    guardian_name = db.Column(db.String(100))
    guardian_contact = db.Column(db.String(20))

    classroom = relationship('Classroom', back_populates='students')
    fee_payments = relationship('FeePayment', backref='student', lazy=True)
    attendance_records = relationship('AttendanceRecord', backref='student', lazy=True)

    def __repr__(self):
        return f"<Student {self.name}>"


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'Present' or 'Absent'

    def __repr__(self):
        return f"<AttendanceRecord {self.date} - Student {self.student_id} - {self.status}>"


class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=date.today, nullable=False)
    term = db.Column(db.String(20), nullable=False)  # 'Term 1', 'Term 2', etc.

    def __repr__(self):
        return f"<FeePayment Student {self.student_id} - {self.amount} KES on {self.payment_date}>"
