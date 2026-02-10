from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import (
    DataRequired, 
    Email, 
    EqualTo, 
    Length, 
    ValidationError,
    NumberRange
)
from app.models import User


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', 
                          validators=[
                              DataRequired(), 
                              Length(min=3, max=80)
                          ])
    email = StringField('Email', 
                       validators=[
                           DataRequired(), 
                           Email(),
                           Length(max=120)
                       ])
    password = PasswordField('Password', 
                            validators=[
                                DataRequired(),
                                Length(min=6, message='Password must be at least 6 characters')
                            ])
    password2 = PasswordField('Confirm Password', 
                             validators=[
                                 DataRequired(),
                                 EqualTo('password', message='Passwords must match')
                             ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists"""
        if user := User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        if user := User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered. Please use a different one.')


class SettingsForm(FlaskForm):
    """User settings form"""
    work_duration = IntegerField('Work Duration (minutes)', 
                                validators=[
                                    DataRequired(),
                                    NumberRange(min=1, max=60)
                                ],
                                default=25)
    short_break_duration = IntegerField('Short Break (minutes)', 
                                       validators=[
                                           DataRequired(),
                                           NumberRange(min=1, max=30)
                                       ],
                                       default=5)
    long_break_duration = IntegerField('Long Break (minutes)', 
                                      validators=[
                                          DataRequired(),
                                          NumberRange(min=1, max=60)
                                      ],
                                      default=15)
    long_break_interval = IntegerField('Long Break After (pomodoros)', 
                                      validators=[
                                          DataRequired(),
                                          NumberRange(min=2, max=10)
                                      ],
                                      default=4)
    
    auto_start_breaks = BooleanField('Auto-start Breaks')
    auto_start_pomodoros = BooleanField('Auto-start Pomodoros')
    notifications_enabled = BooleanField('Enable Notifications')
    sound_enabled = BooleanField('Enable Sound')
    
    submit = SubmitField('Save Settings')