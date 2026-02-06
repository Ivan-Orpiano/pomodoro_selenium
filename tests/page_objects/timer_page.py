# Timer page object
from selenium.webdriver.common.by import By
from tests.page_objects.base_page import BasePage
import time


class TimerPage(BasePage):
    """Page object for the Pomodoro timer page"""
    
    # URL
    PAGE_URL = "/"
    
    # Locators using data-testid for stability
    TIMER_DISPLAY = (By.CSS_SELECTOR, "[data-testid='timer-display']")
    TIMER_STATUS = (By.CSS_SELECTOR, "[data-testid='timer-status']")
    START_BUTTON = (By.CSS_SELECTOR, "[data-testid='start-button']")
    PAUSE_BUTTON = (By.CSS_SELECTOR, "[data-testid='pause-button']")
    RESET_BUTTON = (By.CSS_SELECTOR, "[data-testid='reset-button']")
    SESSION_COUNT = (By.CSS_SELECTOR, "[data-testid='session-count']")
    PROGRESS_BAR = (By.CSS_SELECTOR, "[data-testid='progress-bar']")
    
    # Session type indicators
    WORK_SESSION_INDICATOR = (By.CSS_SELECTOR, "[data-testid='work-session']")
    SHORT_BREAK_INDICATOR = (By.CSS_SELECTOR, "[data-testid='short-break']")
    LONG_BREAK_INDICATOR = (By.CSS_SELECTOR, "[data-testid='long-break']")
    
    # Settings and navigation
    SETTINGS_BUTTON = (By.CSS_SELECTOR, "[data-testid='settings-button']")
    DASHBOARD_LINK = (By.CSS_SELECTOR, "[data-testid='dashboard-link']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "[data-testid='logout-button']")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = self.base_url + self.PAGE_URL
    
    # Navigation methods
    
    def navigate(self):
        """Navigate to timer page"""
        self.navigate_to(self.url)
        self.wait_for_page_load()
    
    # Timer control methods
    
    def start_timer(self):
        """Click start button to begin timer"""
        self.click_element(self.START_BUTTON)
    
    def pause_timer(self):
        """Click pause button to pause timer"""
        self.click_element(self.PAUSE_BUTTON)
    
    def reset_timer(self):
        """Click reset button to reset timer"""
        self.click_element(self.RESET_BUTTON)
    
    # Timer state getters
    
    def get_timer_value(self):
        return self.get_element_text(self.TIMER_DISPLAY)
    
    def get_timer_status(self):
        return self.get_element_text(self.TIMER_STATUS)
    
    def get_session_count(self):

        count_text = self.get_element_text(self.SESSION_COUNT)
        return int(count_text)
    
    def get_progress_percentage(self):
        """
        Get progress bar percentage
        Returns:
            Float percentage (0-100)
        """
        width = self.get_element_attribute(self.PROGRESS_BAR, 'style')
        # Extract percentage from style="width: XX%"
        if 'width' in width:
            return float(width.split(':')[1].strip().rstrip('%;'))
        return 0.0
    
    # Timer state checkers
    
    def is_timer_running(self, wait_seconds=2):
        initial_value = self.get_timer_value()
        time.sleep(wait_seconds)
        current_value = self.get_timer_value()
        return initial_value != current_value
    
    def wait_for_timer_change(self, initial_value, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            current = self.get_timer_value()
            if current != initial_value:
                return True
            time.sleep(0.1)
        return False
    
    def is_start_button_visible(self):
        """Check if start button is visible"""
        return self.is_element_visible(self.START_BUTTON, timeout=2)
    
    def is_pause_button_visible(self):
        """Check if pause button is visible"""
        return self.is_element_visible(self.PAUSE_BUTTON, timeout=2)
    
    def is_reset_button_visible(self):
        """Check if reset button is visible"""
        return self.is_element_visible(self.RESET_BUTTON, timeout=2)
    
    # Session type methods
    
    def is_work_session_active(self):
        """Check if current session is work session"""
        return self.is_element_visible(self.WORK_SESSION_INDICATOR, timeout=2)
    
    def is_short_break_active(self):
        """Check if current session is short break"""
        return self.is_element_visible(self.SHORT_BREAK_INDICATOR, timeout=2)
    
    def is_long_break_active(self):
        """Check if current session is long break"""
        return self.is_element_visible(self.LONG_BREAK_INDICATOR, timeout=2)
    
    # Helper methods
    
    def parse_timer_to_seconds(self, timer_string):
        parts = timer_string.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        return (minutes * 60) + seconds
    
    def wait_for_session_complete(self, timeout=30):
        start_time = time.time()
        initial_count = self.get_session_count()
        
        while time.time() - start_time < timeout:
            current_count = self.get_session_count()
            if current_count > initial_count:
                return True
            time.sleep(0.5)
        
        return False
    
    def get_timer_in_seconds(self):

        timer_value = self.get_timer_value()
        return self.parse_timer_to_seconds(timer_value)
    
    # Navigation methods
    
    def go_to_dashboard(self):
        """Navigate to dashboard"""
        self.click_element(self.DASHBOARD_LINK)
    
    def go_to_settings(self):
        """Navigate to settings"""
        self.click_element(self.SETTINGS_BUTTON)
    
    def logout(self):
        """Logout user"""
        self.click_element(self.LOGOUT_BUTTON)
        