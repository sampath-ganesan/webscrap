from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from selenium.common.exceptions import WebDriverException
import os
import time
import urllib.request
import os.path

class WebDriverManager:
    _instance = None
    _driver = None
    _retry_count = 3
    _retry_delay = 2  # seconds
    _extension_path = os.path.join(os.path.dirname(__file__), 'adblocker_ultimate.crx')

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
            
    def _check_extension(self):
        """Check if the AdBlocker Ultimate extension exists"""
        if not os.path.exists(self._extension_path):
            self.logger.warning("AdBlocker Ultimate extension not found at: " + self._extension_path)
            self.logger.info("Please download the extension and save it as 'adblocker_ultimate.crx' in the utils directory")

    def _create_chrome_options(self):
        chrome_options = Options()
        
        # Set Chrome binary location
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.environ.get('CHROME_PATH')
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if path and os.path.exists(path):
                chrome_binary = path
                break
                
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
        else:
            self.logger.warning("Chrome binary not found in common locations. Please set CHROME_PATH environment variable.")
          
        
        # Add AdBlocker Ultimate extension if available
        if os.path.exists(self._extension_path):
            chrome_options.add_extension(self._extension_path)
            self.logger.info("AdBlocker Ultimate extension added")
        
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--log-level=0')
        # Essential options for stability
        # chrome_options.add_argument('--headless=new')  # New headless mode
        chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        
        # Options to help bypass bot detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add custom preferences to appear more human-like
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'webrtc.ip_handling_policy': 'disable_non_proxied_udp',
            'webrtc.multiple_routes_enabled': False,
            'webrtc.nonproxied_udp_enabled': False
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Additional stability options
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

    def _mask_selenium_properties(self):
        """Mask Selenium's presence by modifying navigator properties"""
        mask_scripts = [
            # Remove webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            # Add chrome plugins
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
            # Add chrome.runtime
            "window.chrome = { runtime: {} }",
            # Modify permissions
            "const originalQuery = window.navigator.permissions.query; window.navigator.permissions.query = parameters => parameters.name === 'notifications' ? Promise.resolve({state: Notification.permission}) : originalQuery(parameters)"
        ]
        for script in mask_scripts:
            try:
                self._driver.execute_script(script)
            except Exception as e:
                self.logger.warning(f"Failed to execute masking script: {str(e)}")

    def get_driver(self):
        try:
            if self._driver is None:
                self.logger.info("Initializing new WebDriver instance...")
                self._check_extension()
                chrome_options = self._create_chrome_options()
                
                try:
                    self._driver = webdriver.Chrome(options=chrome_options)
                    self._driver.set_page_load_timeout(30)  # Set page load timeout
                    self._mask_selenium_properties()  # Apply masking after driver creation
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
