from flask import Flask
from flask_login import LoginManager
from .config import Config
import logging
from pathlib import Path

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'main.candidate_dashboard'  # Updated to use blueprint endpoint

def create_app():
    """Application factory with proper initialization sequence"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    login_manager.init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Ensure upload folder exists
    ensure_upload_folder(app)
    
    return app

def configure_logging(app):
    """Set up application logging"""
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'interview_assistant.log'),
            logging.StreamHandler()
        ]
    )
    app.logger.handlers.extend(logging.getLogger().handlers)

def register_blueprints(app):
    """Register all blueprints with the app"""
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Import models after app creation to avoid circular imports
    from . import models

def ensure_upload_folder(app):
    """Create upload folder if it doesn't exist"""
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(parents=True, exist_ok=True)
