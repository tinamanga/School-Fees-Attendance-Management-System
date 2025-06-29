from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import Config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


jwt = JWTManager()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt.init_app(app)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    app.config["JWT_SECRET_KEY"] = "3e5d1546cc6e02e4185615e8cfafafadbc1f84237a28bcdc220b885d694876f0"  

    # CORS config: allow all methods and headers from React frontend
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    #  Register routes
    from app.routes import init_routes
    init_routes(app)

    
    from app import models

    return app
