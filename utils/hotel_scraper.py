from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
from utils.helpers.login_helper import LoginHelper
from utils.web_driver_manager import WebDriverManager
from utils.config import Config
from bs4 import BeautifulSoup
import requests
import logging
import time
import sys
import itertools
from urllib.parse import urlparse, parse_qs

class HotelScraper:
    def __init__(self):
        self.driver_manager = WebDriverManager()
        self._setup_logging()
        self._max_retries = 2
        self._retry_delay = 2  # seconds
        self.dest_id = None
        self.dest_type = None

    def _setup_logging(self):
        self.logger = logging.getLogger('HotelScraper')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def _show_loading_animation(self, message):
        """Display an animated loading indicator"""
        for frame in itertools.cycle(Config.LOADING_FRAMES):
            sys.stdout.write(f'\r{frame} {message}...')
            sys.stdout.flush()
            time.sleep(Config.LOADING_DELAY)
            yield

    def login(self):
        """Login to Booking.com using email and password."""
        if Config.DO_LOGING:
            self.logger.info("Starting login process")
            try:
                login_helper = LoginHelper()
                login_helper.login_with_email()
                self.logger.info("Login successful")
            except Exception as e:
                self.logger.error(f"Login failed: {str(e)}")
                raise

    def get_destination_info(self, search_term):
        """Get destination ID and type from search term"""
        driver = self.driver_manager.get_driver()
        
        try:
            initial_url = f"{Config.BOOKING_BASE_URL}?ss={search_term}"
            self.logger.info(f"Getting destination info for: {search_term}")
            driver.get(initial_url)
            time.sleep(3)
            
            # Click search button
            search_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button/span[text()='Search']/parent::button"))
            )
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)
            
            # Parse URL for destination info
            current_url = driver.current_url
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            
            dest_id = query_params.get('dest_id', [None])[0]
            dest_type = query_params.get('dest_type', [None])[0]
            
            if dest_id and dest_type:
                self.logger.info(f"Found destination info: ID={dest_id}, Type={dest_type}")
                return dest_id, dest_type
                
        except Exception as e:
            self.logger.error(f"Error getting destination info: {str(e)}")
            return None, None
        
        return None, None

    def get_hotel_pricing(self, params=None):
        self.login()
        """Get hotel pricing with improved scraping and error handling"""
        if params is None:
            params = {
                "ss": "Chennai, India",
                "checkin": "2025-07-15",
                "checkout": "2025-07-17",
                "group_adults": "2",
                "no_rooms": "1",
                "group_children": "0"
            }

        if not self.dest_id or not self.dest_type:
            # Get destination info
            self.dest_id, self.dest_type = self.get_destination_info(params["ss"])
            if not self.dest_id or not self.dest_id:
                self.logger.error("Could not find destination information")
                return []

        # Update parameters with destination info
        params.update({
            "ssne": params["ss"].split(",")[0],
            "ssne_untouched": params["ss"].split(",")[0],
            "efdco": "1",
            "aid": Config.AID,
            "lang": Config.LANG,
            "sb": "1",
            "src_elem": "sb",
            "src": Config.SRC,
            "dest_id": self.dest_id,
            "dest_type": self.dest_type,
            "order": Config.SORT_ORDER,
        })
        filter_params = params.get("filter", None)
        
        for attempt in range(self._max_retries):
            try:
                driver = self.driver_manager.get_driver()
                query_string = '&'.join([f"{k}={v}" for k, v in params.items() if k != 'filter'])
                url = f"{Config.BOOKING_BASE_URL}?{query_string}"
                if filter_params is not None:
                    filter_url = ";".join(f'{i}' for i in filter_params)
                    encoded_filter_url = urllib.parse.quote(filter_url, safe=':/?&')
                    url = url + "&nflt=" + encoded_filter_url
                self.logger.info(f"Fetching URL: {url}")
                loading_animation = self._show_loading_animation("Loading page")
                driver.get(url)
                time.sleep(5)

                # Scroll to load more content
                self.logger.info("Scrolling to load more content...")
                last_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(Config.MAX_SCROLL_ATTEMPTS):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(Config.SCROLL_PAUSE_TIME)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                hotel_results = []

                # Find all property cards
                for index, el in enumerate(soup.find_all("div", {"data-testid": "property-card"}), 1):
                    try:
                        hotel_data = {
                            "serial_no": index,
                            "name": el.find("div", {"data-testid": "title"}).text.strip() if el.find("div", {"data-testid": "title"}) else "",
                            "link": el.find("a", {"data-testid": "title-link"})["href"] if el.find("a", {"data-testid": "title-link"}) else "",
                            "location": el.find("span", {"data-testid": "address"}).text.strip() if el.find("span", {"data-testid": "address"}) else "",
                            "pricing": el.find("span", {"data-testid": "price-and-discounted-price"}),
                            "tax": el.find("div", {"data-testid": "taxes-and-charges"}).text.replace("taxes and fees", "") if el.find("div", {"data-testid": "taxes-and-charges"}) else "",
                            "review": None
                        }

                        # Extract review score
                        hotel_data["review"] = el.select_one('a[data-testid="review-score-link"] > span > div > div:nth-child(2)').text
                        hotel_data["review_count"] = el.select_one('a[data-testid="review-score-link"] > span > div > div:nth-child(3) > div:nth-child(2)').text
                        hotel_results.append(hotel_data)
                    except Exception as e:
                        self.logger.warning(f"Error processing hotel card: {str(e)}")
                        continue

                if hotel_results:
                    self.logger.info(f"Successfully scraped {len(hotel_results)} hotels")
                    return hotel_results

                if attempt < self._max_retries - 1:
                    self.logger.warning(f"No results found, retry attempt {attempt + 1}")
                    time.sleep(self._retry_delay)
                    continue

            except Exception as e:
                self.logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay)
                    continue
                raise

        return []

    def get_filter_details(self, search_term):
        try:
            # Set up headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }

            initial_url = f"{Config.BOOKING_BASE_URL}?ss={search_term}"
            response = requests.get(initial_url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch page. Status code: {response.status_code}")
                return None

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize dictionary to store filter details
            filter_details = {
                'all': [],               
            }

            all_filters = soup.find_all('div', {'data-testid': 'filters-group-label-content'})
            all_value = soup.find_all('', ())
            for rating, value in all_filters, all_value:
                if rating.text:
                    filter_details['all'].append({
                        'name': rating.text,     
                        'value': value.text       
                    })
                        
            return filter_details
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching filter details: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing filter details: {str(e)}")
            return None