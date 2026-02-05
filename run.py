import os
import sys
from app import create_app, db
from app.models import User, PomodoroSession


# Get configuration from environment or use default
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(f'config.{config_name.capitalize()}Config')


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'PomodoroSession': PomodoroSession
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized successfully!')


@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    # Create test user
    test_user = User(username='demo', email='demo@example.com')
    test_user.set_password('demo123')
    
    db.session.add(test_user)
    db.session.commit()
    
    print('Database seeded with sample data!')
    print('Demo user credentials:')
    print('  Username: demo')
    print('  Password: demo123')


if __name__ == '__main__':
    # Create instance folder if it doesn't exist
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)