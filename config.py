import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent
load_dotenv(basedir.parent / '.env')

class Config:
    # Required Configurations
    UPLOAD_FOLDER = basedir / 'static' / 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # AI Configuration
    HUGGINGFACE_TOKEN = os.getenv('HF_TOKEN')
    LLM_MODEL = os.getenv('LLM_MODEL', 'google/gemma-2b-it')
    
    # Auto-generated secret key (no need to set in .env)
    SECRET_KEY = os.urandom(24).hex()

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        if os.getenv('ENABLE_MPS') == 'true':
            os.environ['PYTORCH_ENABLE_MPS'] = '1'
