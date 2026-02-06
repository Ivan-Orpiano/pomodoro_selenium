"""
Timer Functionality Tests
"""
import pytest
import time

from selenium.webdriver.chrome.webdriver import WebDriver
# sourcery skip: dont-import-test-modules
from tests.page_objects.timer_page import TimerPage


@pytest.mark.smoke
def test_timer_page_loads(driver: WebDriver):
    """Test that timer page loads successfully"""
    page = TimerPage(driver)
    page.navigate()
    
    # Verify key elements are visible
    assert page.is_element_visible(page.TIMER_DISPLAY)
    assert page.is_element_visible(page.START_BUTTON)
    assert page.get_timer_value() == "25:00"


@pytest.mark.smoke
def test_timer_starts_countdown(driver: WebDriver):
    """Test that timer starts counting down when start button is clicked"""
    page = TimerPage(driver)
    page.navigate()
    
    # Get initial timer value
    initial_time = page.get_timer_value()
    
    # Start timer
    page.start_timer()
    
    # Verify timer is counting down
    assert page.is_timer_running(wait_seconds=2)
    
    # Verify time has decreased
    current_time = page.get_timer_value()
    assert current_time != initial_time


@pytest.mark.ui
def test_start_button_changes_to_pause(driver: WebDriver):
    """Test that start button becomes pause button when timer starts"""
    page = TimerPage(driver)
    page.navigate()
    
    # Initially start button should be visible
    assert page.is_start_button_visible()
    
    # Start timer
    page.start_timer()
    
    # Pause button should now be visible
    assert page.is_pause_button_visible()


@pytest.mark.regression
def test_pause_timer_functionality(driver: WebDriver):
    """Test that timer can be paused and resumed"""
    page = TimerPage(driver)
    page.navigate()
    
    # Start timer
    page.start_timer()
    time.sleep(2)
    
    # Pause timer
    page.pause_timer()
    paused_time = page.get_timer_value()
    
    # Wait and verify timer is not running
    time.sleep(2)
    assert page.get_timer_value() == paused_time
    
    # Resume timer
    page.start_timer()
    
    # Verify timer is running again
    assert page.is_timer_running(wait_seconds=2)


@pytest.mark.regression
def test_reset_timer_functionality(driver: WebDriver):
    """Test that timer can be reset to initial state"""
    page = TimerPage(driver)
    page.navigate()
    
    initial_value = page.get_timer_value()
    
    # Start timer and let it run
    page.start_timer()
    time.sleep(3)
    
    # Verify timer has changed
    assert page.get_timer_value() != initial_value
    
    # Reset timer
    page.reset_timer()
    
    # Verify timer is back to initial state
    assert page.get_timer_value() == initial_value


@pytest.mark.regression
def test_timer_counts_down_correctly(driver: WebDriver):
    """Test that timer counts down by seconds correctly"""
    page = TimerPage(driver)
    page.navigate()
    
    # Start timer
    page.start_timer()
    
    # Get initial time in seconds
    initial_seconds = page.get_timer_in_seconds()
    
    # Wait 3 seconds
    time.sleep(3)
    
    # Get current time in seconds
    current_seconds = page.get_timer_in_seconds()
    
    # Verify approximately 3 seconds have elapsed (allow 1 second tolerance)
    elapsed = initial_seconds - current_seconds
    assert 2 <= elapsed <= 4


@pytest.mark.ui
def test_timer_status_displays_correctly(driver: WebDriver):
    """Test that timer status message displays correctly"""
    page = TimerPage(driver)
    page.navigate()
    
    # Check initial status
    status = page.get_timer_status()
    assert len(status) > 0  # Status should have some text
    
    # Start timer
    page.start_timer()
    
    # Status should still be visible
    assert page.is_element_visible(page.TIMER_STATUS)


@pytest.mark.regression
def test_session_counter_initial_state(driver: WebDriver):
    """Test that session counter starts at 0"""
    page = TimerPage(driver)
    page.navigate()
    
    # Verify session count is 0
    assert page.get_session_count() == 0


@pytest.mark.ui
def test_progress_bar_visible(driver: WebDriver):
    """Test that progress bar is visible"""
    page = TimerPage(driver)
    page.navigate()
    
    # Verify progress bar element exists
    assert page.is_element_visible(page.PROGRESS_BAR)


@pytest.mark.slow
@pytest.mark.regression
def test_timer_completes_session(driver: WebDriver):
    """Test that timer completes a full session (shortened for testing)"""
    page = TimerPage(driver)
    page.navigate()
    
    # Note: This test assumes test config uses 1-minute sessions
    initial_count = page.get_session_count()
    
    # Start timer
    page.start_timer()
    
    # Wait for session to complete (with timeout)
    completed = page.wait_for_session_complete(timeout=90)
    
    assert completed, "Session did not complete within timeout"
    assert page.get_session_count() == initial_count + 1


@pytest.mark.regression
def test_multiple_pause_resume_cycles(driver: WebDriver):
    """Test multiple pause and resume cycles"""
    page = TimerPage(driver)
    page.navigate()
    
    page.start_timer()
    
    # Perform multiple pause/resume cycles
    for _ in range(3):
        time.sleep(1)
        page.pause_timer()
        paused_time = page.get_timer_value()
        
        time.sleep(1)
        assert page.get_timer_value() == paused_time
        
        page.start_timer()
        time.sleep(1)


@pytest.mark.ui
def test_reset_while_running(driver: WebDriver):
    """Test reset functionality while timer is running"""
    page = TimerPage(driver)
    page.navigate()
    
    initial_value = "25:00"
    
    # Start timer
    page.start_timer()
    time.sleep(2)
    
    # Reset while running
    page.reset_timer()
    
    # Verify reset to initial state
    assert page.get_timer_value() == initial_value


@pytest.mark.ui
def test_reset_while_paused(driver: WebDriver):
    """Test reset functionality while timer is paused"""
    page = TimerPage(driver)
    page.navigate()
    
    initial_value = "25:00"
    
    # Start and pause timer
    page.start_timer()
    time.sleep(2)
    page.pause_timer()
    
    # Reset while paused
    page.reset_timer()
    
    # Verify reset to initial state
    assert page.get_timer_value() == initial_value