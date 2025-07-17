from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from selenium.common.exceptions import WebDriverException
import os
import time

class WebDriverManager:
    _instance = None
    _driver = None
    _retry_count = 3
    _retry_delay = 2  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebDriverManager, cls).__new__(cls)
            cls._instance._setup_logging()
        return cls._instance

    def _setup_logging(self):
        self.logger = logging.getLogger('WebDriverManager')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _create_chrome_options(self):
        chrome_options = Options()
        
        # Essential options for stability
        # chrome_options.add_argument('--headless=new')  # New headless mode
        chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        
        # Additional stability options
        chrome_options.add_argument('--disable-extensions')  # Disable extensions
        chrome_options.add_argument('--disable-software-rasterizer')  # Disable software rasterizer
        chrome_options.add_argument('--ignore-certificate-errors')  # Ignore certificate errors
        chrome_options.add_argument('--disable-web-security')  # Disable web security
        chrome_options.add_argument('--allow-running-insecure-content')  # Allow insecure content
        chrome_options.add_argument('--window-size=1920,1080')  # Set window size
        
        # Performance options
        chrome_options.add_argument('--disable-animations')  # Disable animations
        chrome_options.add_argument('--disable-notifications')  # Disable notifications
        chrome_options.add_argument('--disable-logging')  # Disable logging
        
        # Set user agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
        
        return chrome_options

    def get_driver(self):
        try:
            if self._driver is None:
                self.logger.info("Initializing new WebDriver instance...")
                chrome_options = self._create_chrome_options()
                
                try:
                    self._driver = webdriver.Chrome(options=chrome_options)
                    self._driver.set_page_load_timeout(30)  # Set page load timeout
                    self.logger.info("WebDriver initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
                    raise
            
            # Test if driver is responsive
            try:
                self._driver.current_url
                return self._driver
            except:
                self.logger.warning("Existing driver unresponsive, recreating...")
                self.quit_driver()
                
        except WebDriverException as e:
            self.quit_driver()
            time.sleep(self._retry_delay)
                    
        return self._driver

    def quit_driver(self):
        """Safely quit the WebDriver instance"""
        try:
            if self._driver:
                self.logger.info("Quitting WebDriver...")
                self._driver.quit()
        except Exception as e:
            self.logger.error(f"Error while quitting WebDriver: {str(e)}")
        finally:
            self._driver = None

    def __del__(self):
        """Ensure driver is quit when the instance is deleted"""
        self.quit_driver()
