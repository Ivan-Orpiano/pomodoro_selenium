from datetime import timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import User, PomodoroSession, UserSettings
from app.forms import LoginForm, RegistrationForm, SettingsForm

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page with timer"""
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('main.login'))
        
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default settings for user
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)


@main.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics"""
    # Calculate statistics
    today = datetime.now(timezone.utc).date()
    week_ago = today - timedelta(days=7)

    # Today's sessions
    today_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True,
        func.date(PomodoroSession.started_at) == today
    ).count()

    # This week's sessions
    week_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True,
        func.date(PomodoroSession.started_at) >= week_ago
    ).count()

    # Total sessions
    total_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True
    ).count()

    # Total focus time (in hours)
    total_duration = db.session.query(
        func.sum(PomodoroSession.duration)
    ).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True
    ).scalar() or 0

    total_hours = round(total_duration / 60, 1)

    stats = {
        'today_sessions': today_sessions,
        'week_sessions': week_sessions,
        'total_sessions': total_sessions,
        'total_hours': total_hours
    }

    # Weekly data for chart
    weekly_data = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = PomodoroSession.query.filter(
            PomodoroSession.user_id == current_user.id,
            PomodoroSession.session_type == 'work',
            PomodoroSession.completed == True,
            func.date(PomodoroSession.started_at) == day
        ).count()
        weekly_data.append(count)

    # Recent sessions
    recent_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id
    ).order_by(
        PomodoroSession.started_at.desc()
    ).limit(10).all()

    return render_template('dashboard.html',
                         stats=stats,
                         weekly_data=weekly_data,
                         recent_sessions=recent_sessions)


@main.route('/history')
@login_required
def history():
    """Full session history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id
    ).order_by(
        PomodoroSession.started_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', sessions=sessions)


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()
    
    form = SettingsForm(obj=user_settings)
    
    if form.validate_on_submit():
        form.populate_obj(user_settings)
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('settings.html', form=form, settings=user_settings)


# API Routes for AJAX calls

@main.route('/api/session/start', methods=['POST'])
@login_required
def start_session():
    """Start a new Pomodoro session"""
    data = request.get_json()

    session = PomodoroSession(
        user_id=current_user.id,
        duration=data.get('duration', 25),
        session_type=data.get('session_type', 'work'),
        started_at=datetime.now(timezone.utc),
    )

    db.session.add(session)
    db.session.commit()

    return jsonify({
        'success': True,
        'session_id': session.id
    })


@main.route('/api/session/complete', methods=['POST'])
@login_required
def complete_session():
    """Mark a session as completed"""
    data = request.get_json()

    # Create completed session
    session = PomodoroSession(
        user_id=current_user.id,
        duration=data.get('duration', 25),
        session_type=data.get('session_type', 'work'),
        completed=True,
        started_at=datetime.now(timezone.utc)
        - timedelta(minutes=data.get('duration', 25)),
        completed_at=datetime.now(timezone.utc),
    )

    db.session.add(session)
    db.session.commit()

    # Get updated session count
    total_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True
    ).count()

    return jsonify({
        'success': True,
        'session_id': session.id,
        'total_sessions': total_sessions
    })


@main.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user statistics via API"""
    today = datetime.now(timezone.utc).date()

    today_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True,
        func.date(PomodoroSession.started_at) == today
    ).count()

    total_sessions = PomodoroSession.query.filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.session_type == 'work',
        PomodoroSession.completed == True
    ).count()

    return jsonify({
        'today_sessions': today_sessions,
        'total_sessions': total_sessions
    })


# Error handlers

@main.app_errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('500.html'), 500