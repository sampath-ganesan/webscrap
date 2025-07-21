from utils.web_driver_manager import WebDriverManager
from utils.config import Config
from selenium.webdriver.common.by import By
from utils.helpers.email_helper import EmailHelper
import time
import logging
import itertools

class LoginHelper:
    """Helper class for managing login operations."""
    
    def __init__(self):
        self.driver = WebDriverManager().get_driver()
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger('LoginHelper')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            

    def login_with_email(self):
        """Login to Booking.com using email and password."""
        
        self.driver.get(Config.BOOKING_LOGIN_URL)
        email_input = self.driver.find_element(By.ID, "username")
        email_input.send_keys(Config.EMAIL_ADDRESS)
        continue_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        continue_button.click()
        time.sleep(10)
        otp = EmailHelper.get_otp_from_email()
        self.logger.info(f"OTP received: {otp}")
        if not otp:
            raise Exception("OTP not found in email. Please check your email settings or try again later.")
        
        otp_input = self.driver.find_element(By.CSS_SELECTOR, "[name*=code]")
        otp_chars = list(otp)
        for i in range(len(otp_chars)):            
            self.driver.find_element(By.CSS_SELECTOR, f"[name=code_{i}]").send_keys(otp_chars[i])

        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        time.sleep(5)