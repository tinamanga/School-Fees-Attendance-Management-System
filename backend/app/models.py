from . import db
from sqlalchemy.orm import relationship
from datetime import date

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "admin" or "teacher"

    # Relationships
    attendance_records = relationship('AttendanceRecord', backref='teacher', lazy=True)

    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>"


class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Relationships
    students = relationship('Student', backref='classroom', lazy=True)

    def __repr__(self):
        return f"<Classroom {self.name}>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    guardian_name = db.Column(db.String(100), nullable=False)
    guardian_contact = db.Column(db.String(15), nullable=False)

    # Relationships
    attendance_records = relationship('AttendanceRecord', backref='student', lazy=True)
    fee_payments = relationship('FeePayment', backref='student', lazy=True)

    def __repr__(self):
        return f"<Student {self.name}>"


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # "Present" or "Absent"

    def __repr__(self):
        return f"<AttendanceRecord StudentID={self.student_id} Date={self.date} Status={self.status}>"


class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=date.today, nullable=False)
    term = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<FeePayment StudentID={self.student_id} Amount={self.amount} Term={self.term}>"

