from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache
from config import Config
from .utils.celery_worker import celery_init_app
from .utils import celery_task as tasks

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.login_message_category = 'info'
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
cache = Cache()


def create_app():
    # Create the Flask app instance
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with the app instance
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    # Enable CORS with configuration for the frontend
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:8080"}})

    # Register blueprints for organizing routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.campaigns import campaigns_bp
    app.register_blueprint(campaigns_bp)

    from app.routes.sponsor import sponsor_bp
    app.register_blueprint(sponsor_bp)

    from app.routes.ad_requests import ad_requests_bp
    app.register_blueprint(ad_requests_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.tasks import tasks_bp
    app.register_blueprint(tasks_bp)

    with app.app_context():
        db.create_all()
        create_admin_user()
    
    return app


def create_admin_user():
    from app.models import User
    from werkzeug.security import generate_password_hash

    # Check if the admin user already exists
    existing_admin = User.query.filter_by(username='Admin').first()
    if existing_admin is None:
        password = '123'  # Default admin passwordS
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        admin = User(username='Admin', email='admin@gmail.com', password=hashed_password, role='admin', active=True)
        db.session.add(admin)
        db.session.commit()