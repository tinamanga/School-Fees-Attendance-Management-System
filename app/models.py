from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False,default="student")  # "admin", "teacher", "student"

    attendance_records = db.relationship('AttendanceRecord', backref='teacher', lazy=True)

    def set_password(self, plaintext_password):
        self.password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def check_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)

    def __repr__(self):
        return f"<User {self.username}>"


class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    students = db.relationship('Student', backref='classroom', lazy=True)

    def __repr__(self):
        return f"<Classroom {self.name}>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    guardian_name = db.Column(db.String(120), nullable=False)
    guardian_contact = db.Column(db.String(15), nullable=False)

    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    fee_payments = db.relationship('FeePayment', backref='student', lazy=True, cascade="all, delete")
    user = db.relationship("User", backref="student_profile")

    def __repr__(self):
        return f"<Student {self.name}>"


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False)  # "Present" or "Absent"

    def __repr__(self):
        return f"<AttendanceRecord student_id={self.student_id} date={self.date} status={self.status}>"


class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow)
    term = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<FeePayment student_id={self.student_id} amount={self.amount}>"

