
class Config:
    # Booking.com configuration
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
