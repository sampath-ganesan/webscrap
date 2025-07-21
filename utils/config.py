
class Config:
    # Booking.com configuration
    BOOKING_LOGIN_URL = "https://account.booking.com/sign-in"
    BOOKING_BASE_URL = "https://www.booking.com/searchresults.html"
    SORT_ORDER = "price"
    AID = "7342860"
    LANG = "en-us"
    SRC = "searchresults"
    # Scraping configuration
    SCROLL_PAUSE_TIME = 3
    MAX_SCROLL_ATTEMPTS = 5

    # Animation frames for loading
    LOADING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    LOADING_DELAY = 0.1  # seconds between animation frames

    # Email configuration
    EMAIL_ADDRESS = "sampathprocess@gmail.com"
    EMAIL_PASSWORD = "isou usyn plao oquy"
    EMAIL_IMAP_SERVER = "imap.gmail.com"

    DO_LOGING = True

    # Feature Toggles
    GET_FILTER_FROM_WEB_PAGE = False