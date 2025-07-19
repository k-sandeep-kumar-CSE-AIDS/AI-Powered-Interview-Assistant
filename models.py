from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime
import os
import json
from pathlib import Path
import logging
from . import login_manager

# Constants
USERS_FILE = 'instance/users.json'
SESSIONS_FILE = 'instance/sessions.json'

class User(UserMixin):
    def __init__(self, id, username, email, password, role='candidate'):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.resume_text = ""
        self.generated_questions = ""
        self.interview_history = []
    
    def check_password(self, password):
        """Securely check password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Save user data to JSON file"""
        try:
            users = User.get_all_users()
            users[self.id] = {
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'role': self.role,
                'resume_text': self.resume_text,
                'generated_questions': self.generated_questions,
                'interview_history': self.interview_history
            }
            
            Path(USERS_FILE).parent.mkdir(exist_ok=True)
            with open(USERS_FILE, 'w') as f:
                json.dump(users, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error saving user {self.id}: {str(e)}")
            raise

    @staticmethod
    def get(user_id):
        """Retrieve user by ID"""
        try:
            users = User.get_all_users()
            if user_data := users.get(user_id):
                user = User(
                    user_id,
                    user_data['username'],
                    user_data['email'],
                    "placeholder",  # Password not needed for retrieval
                    user_data['role']
                )
                user.resume_text = user_data.get('resume_text', "")
                user.generated_questions = user_data.get('generated_questions', "")
                user.interview_history = user_data.get('interview_history', [])
                return user
            return None
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {str(e)}")
            return None

    @staticmethod
    def get_all_users():
        """Load all users from JSON file"""
        try:
            if Path(USERS_FILE).exists():
                with open(USERS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading users: {str(e)}")
            return {}

class InterviewSession:
    def __init__(self, candidate_id, recruiter_id, job_description):
        self.id = str(uuid.uuid4())
        self.candidate_id = candidate_id
        self.recruiter_id = recruiter_id
        self.job_description = job_description
        self.questions = []
        self.answers = []
        self.evaluation = {}
        self.date = datetime.now().isoformat()
    
    def save(self):
        """Save session data to JSON file"""
        try:
            sessions = InterviewSession.get_all_sessions()
            sessions[self.id] = {
                'candidate_id': self.candidate_id,
                'recruiter_id': self.recruiter_id,
                'job_description': self.job_description,
                'questions': self.questions,
                'answers': self.answers,
                'evaluation': self.evaluation,
                'date': self.date
            }
            
            Path(SESSIONS_FILE).parent.mkdir(exist_ok=True)
            with open(SESSIONS_FILE, 'w') as f:
                json.dump(sessions, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error saving session {self.id}: {str(e)}")
            raise

    @staticmethod
    def get_all_sessions():
        """Load all sessions from JSON file"""
        try:
            if Path(SESSIONS_FILE).exists():
                with open(SESSIONS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading sessions: {str(e)}")
            return {}

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Required callback for Flask-Login"""
    return User.get(user_id)
