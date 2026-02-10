from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and session tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    sessions = db.relationship('PomodoroSession', backref='user', lazy='dynamic', 
                              cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False,
                              cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class PomodoroSession(db.Model):
    """Pomodoro session tracking"""
    __tablename__ = 'pomodoro_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    completed = db.Column(db.Boolean, default=False)
    session_type = db.Column(db.String(20), nullable=False)  # 'work', 'short_break', 'long_break'
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Optional task/note
    task_description = db.Column(db.String(200))
    
    def complete_session(self):
        """Mark session as completed"""
        self.completed = True
        self.completed_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def __repr__(self):
        return f'<PomodoroSession {self.id}: {self.session_type}>'


class UserSettings(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timer durations (in minutes)
    work_duration = db.Column(db.Integer, default=25)
    short_break_duration = db.Column(db.Integer, default=5)
    long_break_duration = db.Column(db.Integer, default=15)
    long_break_interval = db.Column(db.Integer, default=4)
    
    # Preferences
    auto_start_breaks = db.Column(db.Boolean, default=False)
    auto_start_pomodoros = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    
    # Appearance
    theme = db.Column(db.String(20), default='light')  # 'light', 'dark'
    
    def __repr__(self):
        return f'<UserSettings for User {self.user_id}>'
    
    