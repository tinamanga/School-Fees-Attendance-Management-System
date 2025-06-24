from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///school.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from app.routes.students import students_bp
    from app.routes.attendance import attendance_bp
    from app.routes.fees import fees_bp

    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(fees_bp, url_prefix="/fees")

    return app
if __name__=='__main__':
    app.run(debug=True)