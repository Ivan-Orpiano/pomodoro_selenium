#Base Object
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.action_chains import ActionChains
import time


class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)
        self.base_url = "http://localhost:5000"
    
    # Element interaction methods
    
    def find_element(self, locator, timeout=10):
        """
        Find element with explicit wait
        Args:
            locator: Tuple of (By.METHOD, "value")
            timeout: Wait timeout in seconds
        Returns:
            WebElement
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator, timeout=10):
        """Find multiple elements with explicit wait"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)
    
    def click_element(self, locator, timeout=10):

        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def enter_text(self, locator, text, clear_first=True):

        element = self.find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
    
    def get_element_text(self, locator, timeout=10):
        """Get text content of element"""
        element = self.find_element(locator, timeout)
        return element.text
    
    def get_element_attribute(self, locator, attribute, timeout=10):
        """Get attribute value of element"""
        element = self.find_element(locator, timeout)
        return element.get_attribute(attribute)
    
    # Visibility and state checks
    
    def is_element_visible(self, locator, timeout=5):
   
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def is_element_present(self, locator, timeout=5):
        """Check if element is present in DOM"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(self, locator, timeout=5):
        """Check if element is clickable"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.element_to_be_clickable(locator))
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_to_disappear(self, locator, timeout=10):
        """Wait for element to disappear from DOM"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    # Navigation methods
    
    def navigate_to(self, url):
        """Navigate to a URL"""
        self.driver.get(url)
    
    def get_current_url(self):
        """Get current page URL"""
        return self.driver.current_url
    
    def refresh_page(self):
        """Refresh current page"""
        self.driver.refresh()
    
    def go_back(self):
        """Navigate back"""
        self.driver.back()
    
    # Wait methods
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to load completely"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    
    def wait_for_url_change(self, old_url, timeout=10):
        """Wait for URL to change from old_url"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.url_changes(old_url))
    
    def wait_for_url_contains(self, text, timeout=10):
        """Wait for URL to contain specific text"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.url_contains(text))
    
    # JavaScript execution
    
    def execute_script(self, script, *args):
        """Execute JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def scroll_to_element(self, locator):
        """Scroll element into view"""
        element = self.find_element(locator)
        self.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_to_top(self):
        """Scroll to top of page"""
        self.execute_script("window.scrollTo(0, 0);")
    
    # Alert handling
    
    def accept_alert(self, timeout=5):
        """Accept alert dialog"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert.accept()
            return True
        except TimeoutException:
            return False
    
    def dismiss_alert(self, timeout=5):
        """Dismiss alert dialog"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert.dismiss()
            return True
        except TimeoutException:
            return False
    
    def get_alert_text(self, timeout=5):
        """Get alert text"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            return alert.text
        except TimeoutException:
            return None
    
    # Screenshot
    
    def take_screenshot(self, filename):
        """Take screenshot and save to file"""
        self.driver.save_screenshot(filename)
    
    # Retry mechanism for flaky tests
    
    def retry_on_stale_element(self, func, max_attempts=3):
        """
        Retry function if StaleElementReferenceException occurs
        Useful for dynamic content
        """
        for attempt in range(max_attempts):
            try:
                return func()
            except StaleElementReferenceException:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(0.5)