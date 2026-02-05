import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models import User, UserSettings
from config import TestConfig


@pytest.fixture(scope='session')
def app():
    """
    Create and configure a test Flask application instance
    Session-scoped: created once for entire test session
    """
    app = create_app(TestConfig)
    
    # Establish application context
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create a test client for the app
    Function-scoped: new client for each test
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def driver():
    """
    Initialize WebDriver for Selenium tests
    Function-scoped: new driver for each test
    """
    options = Options()
    
    # Headless mode for CI/CD
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Disable unnecessary features
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    
    # Additional stability options
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Initialize driver with automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set implicit wait
    driver.implicitly_wait(10)
    
    yield driver
    
    # Cleanup
    driver.quit()


@pytest.fixture(scope='function')
def test_user(app):
    """
    Create a test user in the database
    Function-scoped: new user for each test
    """
    with app.app_context():
        # Create user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Create default settings for user
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        user_id = user.id
        
        yield user
        
        # Cleanup
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()


@pytest.fixture(scope='function')
def authenticated_user(client, test_user):
    """
    Create and authenticate a test user
    Returns tuple: (client, user)
    """
    # Login the test user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    return client, test_user


@pytest.fixture(scope='function')
def multiple_users(app):
    """
    Create multiple test users
    Returns list of user objects
    """
    with app.app_context():
        users = []
        
        for i in range(3):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        
        yield users
        
        # Cleanup
        for user in users:
            db.session.delete(user)
        db.session.commit()


@pytest.fixture(autouse=True)
def reset_db(app):
    """
    Reset database between tests
    Autouse: runs automatically for every test
    """
    with app.app_context():
        yield
        # Rollback any uncommitted changes
        db.session.rollback()


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "smoke: Quick smoke tests for critical functionality"
    )
    config.addinivalue_line(
        "markers", "regression: Full regression test suite"
    )
    config.addinivalue_line(
        "markers", "ui: UI-focused tests"
    )
    config.addinivalue_line(
        "markers", "admin: Tests requiring admin access"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to execute"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test failures and take screenshots
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Only capture on test call (not setup/teardown)
    if rep.when == 'call' and rep.failed:
        # Get driver from test if available
        driver = item.funcargs.get('driver')
        
        if driver:
            # Create screenshots directory if it doesn't exist
            screenshot_dir = 'reports/screenshots'
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Save screenshot
            screenshot_path = f'{screenshot_dir}/{item.name}.png'
            driver.save_screenshot(screenshot_path)
            
            # Save page source for debugging
            html_path = f'{screenshot_dir}/{item.name}.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)