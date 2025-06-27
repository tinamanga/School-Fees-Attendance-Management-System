from flask import Flask, request, make_response, jsonify, send_file
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from twilio.rest import Client

from models import db, User, Student, Classroom, AttendanceRecord, FeePayment

# Twilio credentials (replace with real values in production)
TWILIO_SID = 'your_sid'
TWILIO_TOKEN = 'your_token'
TWILIO_FROM = '+1234567890'
client = Client(TWILIO_SID, TWILIO_TOKEN)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app,supports_credentials=True,origins=["http://localhost:5173"])
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def welcome():
    return "<h1>Server is running</h1>"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        return make_response({
            'message': 'Login successful',
            'role': user.role,
            'username': user.username,
            'id': user.id
        }, 200)
    return make_response({'error': 'Invalid username or password'}, 401)

@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role
    } for u in users])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(key in data for key in ['username', 'email', 'password', 'role']):
        return make_response({'error': 'Missing fields'}, 400)
    hashed_pw = generate_password_hash(data['password'])
    user = User(username=data['username'], email=data['email'], password=hashed_pw, role=data['role'])
    db.session.add(user)
    db.session.commit()
    return make_response({'message': 'User created'}, 201)

@app.route('/dashboard')
def dashboard():
    student_count = Student.query.count()
    total_fees = db.session.query(db.func.sum(FeePayment.amount)).scalar() or 0
    today = date.today()
    total_attendance = AttendanceRecord.query.filter_by(date=today).count()
    present_count = AttendanceRecord.query.filter_by(date=today, status="Present").count()
    attendance_percentage = round((present_count / total_attendance * 100), 2) if total_attendance else 0.0
    return make_response({
        'total_students': student_count,
        'total_fees_collected': total_fees,
        'attendance_today': attendance_percentage
    }, 200)

@app.route('/students', methods=['GET'])
def get_students():
    try:
        classroom_id = request.args.get('classroom_id', type=int)
        min_balance = request.args.get('min_balance', type=int)
        expected_fee_per_term = 10000
        terms = ['Term 1', 'Term 2', 'Term 3']
        expected_total = expected_fee_per_term * len(terms)

        students = Student.query.filter_by(classroom_id=classroom_id).all() if classroom_id else Student.query.all()
        result = []
        for student in students:
            classroom = Classroom.query.get(student.classroom_id)
            total_fees_paid = sum(f.amount for f in student.fee_payments)
            fee_balance = expected_total - total_fees_paid
            if min_balance is not None and fee_balance < min_balance:
                continue
            total_attendance = len(student.attendance_records)
            present_count = sum(1 for r in student.attendance_records if r.status == "Present")
            attendance_percentage = (present_count / total_attendance * 100) if total_attendance else 0
            result.append({
                'id': student.id,
                'name': student.name,
                'classroom_id': student.classroom_id,
                'classroom_name': classroom.name if classroom else None,
                'guardian_name': student.guardian_name,
                'guardian_contact': student.guardian_contact,
                'fees_paid': total_fees_paid,
                'expected_fees': expected_total,
                'fee_balance': fee_balance,
                'attendance_percentage': round(attendance_percentage, 2)
            })
        return make_response(result, 200)
    except Exception as e:
        return make_response({'error': str(e)}, 500)

@app.route('/students/<int:id>', methods=['GET'])
def get_student_by_id(id):
    student = Student.query.get_or_404(id)
    classroom = Classroom.query.get(student.classroom_id)
    attendance = [{'date': r.date.isoformat(), 'status': r.status} for r in student.attendance_records]
    fees = [{'amount': f.amount, 'term': f.term, 'payment_date': f.payment_date.isoformat()} for f in student.fee_payments]
    total_paid = sum(f['amount'] for f in fees)
    expected_total = 30000
    balance = expected_total - total_paid
    return make_response({
        'id': student.id,
        'name': student.name,
        'classroom_name': classroom.name if classroom else None,
        'guardian_name': student.guardian_name,
        'guardian_contact': student.guardian_contact,
        'fees': fees,
        'attendance': attendance,
        'total_paid': total_paid,
        'expected_total': expected_total,
        'balance': balance,
    }, 200)

@app.route('/students/<int:id>/report', methods=['GET'])
def export_student_report(id):
    student = Student.query.get_or_404(id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Report for {student.name}")
    y = 760
    for f in student.fee_payments:
        p.drawString(80, y, f"{f.term}: KES {f.amount} on {f.payment_date}")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, download_name=f"{student.name}_report.pdf", as_attachment=True)

@app.route('/attendance', methods=['POST'])
def record_attendance():
    data = request.get_json()
    record = AttendanceRecord(
        student_id=data['student_id'],
        teacher_id=data['teacher_id'],
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else date.today(),
        status=data['status']
    )
    db.session.add(record)
    db.session.commit()
    return make_response({'message': 'Attendance recorded'}, 201)

@app.route('/attendance', methods=['GET'])
def get_attendance():
    records = AttendanceRecord.query.all()
    return jsonify([{
        "id": r.id,
        "student_id": r.student_id,
        "teacher_id": r.teacher_id,
        "status": r.status,
        "date": r.date.isoformat()
    } for r in records])

@app.route('/fees', methods=['GET'])
def get_fees():
    fees = FeePayment.query.all()
    return make_response([{
        'id': f.id,
        'student_id': f.student_id,
        'amount': f.amount,
        'payment_date': f.payment_date.isoformat(),
        'term': f.term
    } for f in fees], 200)

@app.route('/fees', methods=['POST'])
def record_fee():
    data = request.get_json()
    fee = FeePayment(
        student_id=data['student_id'],
        amount=data['amount'],
        payment_date=datetime.strptime(data.get('payment_date'), '%Y-%m-%d').date() if data.get('payment_date') else date.today(),
        term=data['term']
    )
    db.session.add(fee)
    db.session.commit()
    return make_response({'message': 'Fee payment recorded'}, 201)

@app.route('/alerts/fees-due', methods=['POST'])
def sms_fee_alerts():
    students = Student.query.all()
    results = []
    for s in students:
        total = sum(f.amount for f in s.fee_payments)
        due = 30000 - total
        if due > 0:
            msg = client.messages.create(
                body=f"Hello {s.guardian_name}, your child {s.name} owes KES {due}.",
                from_=TWILIO_FROM,
                to=s.guardian_contact
            )
            results.append({'student': s.id, 'sms_sid': msg.sid})
    return jsonify(results), 200

@app.route('/classrooms')
def get_classrooms():
    classrooms = Classroom.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in classrooms])

@app.route('/reports/classroom/<int:classroom_id>/pdf', methods=['GET'])
def generate_classroom_report_pdf(classroom_id):
    students = Student.query.filter_by(classroom_id=classroom_id).all()
    classroom = Classroom.query.get_or_404(classroom_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(50, 820, f"Classroom Report - {classroom.name}")
    y = 780
    for student in students:
        fees_paid = sum(f.amount for f in student.fee_payments)
        attendance = student.attendance_records
        present = sum(1 for a in attendance if a.status == "Present")
        total_days = len(attendance)
        attendance_pct = (present / total_days * 100) if total_days else 0
        p.drawString(50, y, f"{student.name} | Fees Paid: KES {fees_paid} | Attendance: {round(attendance_pct, 2)}%")
        y -= 20
        if y < 100:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"class_{classroom_id}_report.pdf")

@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = User.query.filter_by(role='teacher').all()
    return jsonify([{
        "id": t.id,
        "username": t.username,
        "email": t.email,
        "subject": t.subject
    } for t in teachers]), 200

@app.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.get_json()
    if not all(k in data for k in ['username', 'email', 'password', 'subject', 'classroom_id']):
        return jsonify({'error': 'Missing fields'}), 400
    hashed_pw = generate_password_hash(data['password'])
    new_teacher = User(
        username=data['username'],
        email=data['email'],
        password=hashed_pw,
        role='teacher',
        subject=data['subject'],
        classroom_id=data['classroom_id']
    )
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify({'message': 'Teacher created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)
