import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from gui.search_frame import SearchFrame
from gui.results_frame import ResultsFrame
from utils.web_driver_manager import WebDriverManager
from utils.hotel_scraper import HotelScraper

class HotelSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Search Application")
        
        # Initialize managers
        self.driver_manager = WebDriverManager()
        self.hotel_scraper = HotelScraper()
        
        # Setup window
        self.setup_window()
        
        # Create main components
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create search frame
        self.search_frame = SearchFrame(self.main_frame)
        self.search_frame.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Create results frame (but don't grid it yet)
        self.results_frame = ResultsFrame(self.main_frame)
        
        # Create "New Search" button frame
        self.button_frame = ttk.Frame(self.main_frame, padding="5")
        self.new_search_button = ttk.Button(self.button_frame, text="New Search", 
                                          command=self.show_search_criteria)
        self.new_search_button.pack(pady=5)
        
        # Create searching label
        self.searching_label = ttk.Label(self.main_frame, 
                                       text="Searching hotels... Please wait...", 
                                       font=('Arial', 12))
        
        # Configure grid weights
        self.setup_grid_weights()
        
        # Add search button to search frame's button frame
        self.search_button = ttk.Button(self.search_frame.buttons_frame, text="Search Hotels", 
                                      command=self.search_hotels)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
    def setup_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.minsize(800, 600)
        self.root.state('zoomed')
        
    def setup_grid_weights(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
    def show_search_criteria(self):
        self.results_frame.frame.grid_remove()
        self.button_frame.grid_remove()
        self.search_frame.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
    def show_searching_message(self):
        self.search_frame.frame.grid_remove()
        self.searching_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.root.update()
        
    def show_error_message(self, error_message):
        # Create error frame
        error_frame = ttk.Frame(self.main_frame, padding="10")
        error_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Show error message
        error_label = ttk.Label(error_frame, 
                               text=f"Error: {error_message}\nPlease try again.", 
                               font=('Arial', 12))
        error_label.pack(pady=20)
        
        # Add Try New Search button
        retry_button = ttk.Button(error_frame, text="Try New Search", 
                                 command=lambda: [error_frame.destroy(), self.show_search_criteria()])
        retry_button.pack(pady=10)
        
    def show_results(self):
        self.search_frame.frame.grid_remove()
        self.searching_label.grid_remove()
        self.results_frame.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.button_frame.grid(row=1, column=0, sticky=(tk.E, tk.W), padx=5, pady=5)
        
    def search_hotels(self):
        # Get search parameters
        params = self.search_frame.get_search_params()
        
        # Validate dates
        start_date = datetime.strptime(params['checkin_date'], '%Y-%m-%d')
        end_date = datetime.strptime(params['checkout_date'], '%Y-%m-%d')
        if end_date <= start_date:
            messagebox.showerror("Date Error", "Check-out date must be after check-in date")
            return
            
        self.show_searching_message()
        
        try:
            all_results = []
            
            if params['search_type'] == "single":
                search_params = {
                    "ss": params['destination'],
                    "checkin": params['checkin_date'],
                    "checkout": params['checkout_date'],
                    "group_adults": params['base_adults'],
                    "no_rooms": params['rooms'],
                    "group_children": params['children'],
                    "sb": "1",
                    "src": "searchresults",
                    "src_elem": "sb",
                    "filter": params["filter_params"]
                }
                # Search for each adult count
                for adult_count in params['adult_counts']:
                    search_params['group_adults'] = adult_count
                    hotel_results = self.hotel_scraper.get_hotel_pricing(search_params)
                    if hotel_results:
                        for hotel in hotel_results:
                            hotel['adults'] = adult_count
                        all_results.extend(hotel_results)
                    self.root.after(1000)  # Small delay between requests
            else:
                current_date = start_date
                while current_date < end_date:
                    next_date = current_date + timedelta(days=1)
                    search_params = {
                        "ss": params['destination'],
                        "checkin": current_date.strftime('%Y-%m-%d'),
                        "checkout": next_date.strftime('%Y-%m-%d'),
                        "group_adults": params['base_adults'],  # Use base adults as default
                        "no_rooms": params['rooms'],
                        "group_children": params['children'],
                        "sb": "1",
                        "src": "searchresults",
                        "src_elem": "sb",
                        "filter": params["filter_params"]
                    }
                    
                    # Search for each adult count
                    for adult_count in params['adult_counts']:
                        search_params['group_adults'] = adult_count
                        hotel_results = self.hotel_scraper.get_hotel_pricing(search_params)
                        if hotel_results:
                            for hotel in hotel_results:
                                hotel['date'] = current_date.strftime('%Y-%m-%d')
                                hotel['adults'] = adult_count
                            all_results.extend(hotel_results)
                        self.root.after(1000)  # Small delay between requests
                    
                    current_date = next_date
                    self.root.after(1000)  # Small delay between requests
                    self.root.update()
            
            if not all_results:
                messagebox.showwarning("No Results", "No hotels found for the selected criteria.")
                self.results_frame.show_search_criteria()
                return
            
            self.results_frame.update_results(all_results)
            self.show_results()
            
        except Exception as e:
            self.searching_label.grid_remove()
            self.show_error_message(f"An error occurred while searching: {str(e)}")

def main():
    root = tk.Tk()
    app = HotelSearchApp(root)
    root.mainloop()
    WebDriverManager().quit_driver()

if __name__ == "__main__":
    main()
