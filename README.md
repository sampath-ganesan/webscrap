# Hotel Search Application

A powerful and user-friendly application for scraping and analyzing hotel information using Python and Selenium.

## Features

- GUI-based hotel search interface
- Advanced web scraping capabilities
- Email integration for results
- Google API integration
- Custom filtering options
- Results visualization and export
- Automated browser management with adblock support

## Prerequisites

- Python 3.x
- Chrome browser installed
- Internet connection
- Google API credentials (for email functionality)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sampath-ganesan/webscrap.git
cd webscrap
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google API credentials:
   - Place your `credentials.json` file in the `gui/` directory
   - On first run, the application will guide you through the authentication process
   - The resulting `token.json` will be saved in the `gui/` directory

## Project Structure

```
webscrap/
├── main.py                 # Main application entry point
├── gui/                    # GUI-related components
│   ├── results_frame.py    # Results display interface
│   ├── search_frame.py     # Search criteria interface
│   └── credentials.json    # Google API credentials
├── utils/                  # Utility modules
│   ├── adblocker_ultimate.crx  # Adblock extension
│   ├── config.py          # Configuration settings
│   ├── hotel_scraper.py   # Core scraping functionality
│   ├── web_driver_manager.py   # Selenium browser management
│   ├── helpers/           # Helper modules
│   │   ├── email_helper.py    # Email functionality
│   │   └── login_helper.py    # Authentication handling
│   └── resources/         # Additional resources
│       └── filters.py     # Data filtering utilities
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Using the Search Interface:
   - Enter your destination
   - Select check-in and check-out dates
   - Specify number of guests
   - Add any additional filters
   - Click "Search Hotels"

3. Working with Results:
   - View detailed hotel information
   - Apply filters to refine results
   - Export results to desired format
   - Send results via email

4. Additional Features:
   - Click "New Search" to start a fresh search
   - Use the built-in filtering options to sort results
   - Access saved searches and results

## Configuration

The application can be configured through `utils/config.py`:
- Browser settings
- Search parameters
- Email settings
- API configurations
- Filter preferences

## Troubleshooting

1. Browser Issues:
   - Ensure Chrome is installed
   - Check if the webdriver is compatible with your Chrome version
   - Verify adblocker extension is present

2. Authentication Issues:
   - Confirm credentials.json is properly configured
   - Check token.json permissions
   - Verify internet connection

3. Search Problems:
   - Validate input parameters
   - Check network connectivity
   - Ensure date ranges are valid

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
- Check existing documentation
- Review troubleshooting guide
- Open an issue on GitHub
- Contact the maintainers

## Acknowledgments

- Selenium WebDriver team
- Python community
- Contributors and testers