#!/usr/bin/env python3
import os
import sys
import logging
import webbrowser
from pathlib import Path
from threading import Timer

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app import create_app
from app.config import Config

def configure_logging():
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

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    configure_logging()
    app = create_app()
    Config.init_app(app)

    # Delay browser open to ensure server is up
    Timer(1, open_browser).start()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
