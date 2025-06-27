from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from datetime import date
from models import db, User, Student, Classroom, AttendanceRecord, FeePayment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def welcome():
    return "<h1>running</h1>"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        return make_response({'message': 'Login successful', 'role': user.role}, 200)
    return make_response({'error': 'Invalid username or password'}, 401)

@app.route('/dashboard')
def dashboard():
    student_count = Student.query.count()
    total_fees = db.session.query(db.func.sum(FeePayment.amount)).scalar() or 0
    return make_response({'total_students': student_count, 'total_fees_collected': total_fees}, 200)

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    result = [
        {
            'id': student.id,
            'name': student.name,
            'classroom_id': student.classroom_id,
            'guardian_name': student.guardian_name,
            'guardian_contact': student.guardian_contact
        }
        for student in students
    ]
    return make_response(result, 200)

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    student = Student(
        name=data['name'],
        classroom_id=data['classroom_id'],
        guardian_name=data['guardian_name'],
        guardian_contact=data['guardian_contact']
    )
    db.session.add(student)
    db.session.commit()
    return make_response({'message': 'Student created'}, 201)

@app.route('/attendance', methods=['GET'])
def get_attendance():
    records = AttendanceRecord.query.all()
    result = [
        {
            'id': r.id,
            'student_id': r.student_id,
            'teacher_id': r.teacher_id,
            'date': r.date.isoformat(),
            'status': r.status
        }
        for r in records
    ]
    return make_response(result, 200)

@app.route('/attendance', methods=['POST'])
def record_attendance():
    data = request.get_json()
    record = AttendanceRecord(
        student_id=data['student_id'],
        teacher_id=data['teacher_id'],
        date=data.get('date', date.today()),
        status=data['status']
    )
    db.session.add(record)
    db.session.commit()
    return make_response({'message': 'Attendance recorded'}, 201)

@app.route('/fees', methods=['GET'])
def get_fees():
    fees = FeePayment.query.all()
    result = [
        {
            'id': f.id,
            'student_id': f.student_id,
            'amount': f.amount,
            'payment_date': f.payment_date.isoformat(),
            'term': f.term
        }
        for f in fees
    ]
    return make_response(result, 200)

@app.route('/fees', methods=['POST'])
def record_fee():
    data = request.get_json()
    fee = FeePayment(
        student_id=data['student_id'],
        amount=data['amount'],
        payment_date=data.get('payment_date', date.today()),
        term=data['term']
    )
    db.session.add(fee)
    db.session.commit()
    return make_response({'message': 'Fee payment recorded'}, 201)

if __name__ == '__main__':
        app.run(debug=True)