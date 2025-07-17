import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from utils.hotel_scraper import HotelScraper

class SearchFrame:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.hotel_scraper = HotelScraper()
        self.filter_vars = {}
        
        # Create search criteria frame on the left
        self.search_criteria_frame = ttk.LabelFrame(self.frame, text="Search Criteria", padding="10")
        self.search_criteria_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        
        # Create filter frame on the right
        self.filter_frame = ttk.LabelFrame(self.frame, text="Filters", padding="10")
        self.filter_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        
        # Configure grid weights for the main frame
        self.frame.columnconfigure(0, weight=3)  # Search criteria takes more space
        self.frame.columnconfigure(1, weight=2)  # Filter section takes less space
        self.frame.rowconfigure(0, weight=1)
        
        # Location
        ttk.Label(self.search_criteria_frame, text="Destination:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.destination = ttk.Entry(self.search_criteria_frame, width=40)
        self.destination.insert(0, "Chennai, India")
        self.destination.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Add destination change handler
        self.destination.bind('<FocusOut>', lambda e: self.load_filters())
        
        # Check-in date
        ttk.Label(self.search_criteria_frame, text="Check-in Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.checkin_cal = Calendar(self.search_criteria_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.checkin_cal.grid(row=1, column=1, columnspan=2, pady=5)
        
        # Check-out date
        ttk.Label(self.search_criteria_frame, text="Check-out Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.checkout_cal = Calendar(self.search_criteria_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.checkout_cal.grid(row=2, column=1, columnspan=2, pady=5)
        
        # Adults
        ttk.Label(self.search_criteria_frame, text="Adults:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.adults = ttk.Spinbox(self.search_criteria_frame, from_=1, to=10, width=5)
        self.adults.set(2)
        self.adults.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Rooms
        ttk.Label(self.search_criteria_frame, text="Rooms:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rooms = ttk.Spinbox(self.search_criteria_frame, from_=1, to=5, width=5)
        self.rooms.set(1)
        self.rooms.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Children
        ttk.Label(self.search_criteria_frame, text="Children:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.children = ttk.Spinbox(self.search_criteria_frame, from_=0, to=5, width=5)
        self.children.set(0)
        self.children.grid(row=5, column=1, sticky=tk.W, pady=5)

        # Search Type
        ttk.Label(self.search_criteria_frame, text="Search Type:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.search_type = tk.StringVar(value="single")
        ttk.Radiobutton(self.search_criteria_frame, text="Single Day", variable=self.search_type, 
                       value="single").grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(self.search_criteria_frame, text="Date Range", variable=self.search_type, 
                       value="range").grid(row=6, column=2, sticky=tk.W, pady=5)
                       
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.search_criteria_frame)
        self.buttons_frame.grid(row=7, column=0, columnspan=3, pady=10)

        # Setup filter section
        # Filter header frame
        filter_header = ttk.Frame(self.filter_frame)
        filter_header.pack(fill=tk.X, padx=5, pady=5)
        
        # Title and refresh button
        ttk.Label(filter_header, text="Search Filters:").pack(side=tk.LEFT)
        self.refresh_btn = ttk.Button(filter_header, text="↻", width=3, command=self.refresh_filters)
        self.refresh_btn.pack(side=tk.RIGHT)
        
        # Search Entry frame
        search_frame = ttk.Frame(self.filter_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_search(self.search_var.get()))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Select All checkbox
        self.select_all_var = tk.BooleanVar()
        self.select_all_checkbox = ttk.Checkbutton(self.filter_frame, 
                                                  text="Select All", 
                                                  variable=self.select_all_var,
                                                  command=self.toggle_all_filters)
        self.select_all_checkbox.pack(anchor=tk.W, padx=5, pady=5)
        
        # Create canvas for scrollable content
        self.filter_canvas = tk.Canvas(self.filter_frame)
        filter_scrollbar = ttk.Scrollbar(self.filter_frame, orient="vertical", command=self.filter_canvas.yview)
        self.filters_frame = ttk.Frame(self.filter_canvas)
        
        self.filter_canvas.configure(yscrollcommand=filter_scrollbar.set)
        
        filter_scrollbar.pack(side="right", fill="y")
        self.filter_canvas.pack(side="left", fill="both", expand=True)
        
        self.filter_canvas.create_window((0, 0), window=self.filters_frame, anchor="nw")
        self.filters_frame.bind("<Configure>", lambda e: self.filter_canvas.configure(scrollregion=self.filter_canvas.bbox("all")))
        
        # Add disabled placeholder text
        self.placeholder_label = ttk.Label(self.filters_frame, 
                                         text="Click refresh button (↻) to load filters",
                                         foreground="gray")
        self.placeholder_label.pack(pady=20)
        
        # Disable select all checkbox initially
        self.select_all_checkbox.configure(state='disabled')
        
    def refresh_filters(self):
        """Called when refresh button is clicked"""
        # Clear placeholder if it exists
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.destroy()
            
        # Clear search field
        self.search_var.set('')
            
        # Enable select all checkbox and uncheck it
        self.select_all_checkbox.configure(state='normal')
        self.select_all_var.set(False)
        
        # Destroy all widgets in the filters frame
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
            
        # Clear the filter variables dictionary
        self.filter_vars.clear()
        
        # Load fresh filters
        self.load_filters()
        
    def load_filters(self, *args):
        # Ensure all existing widgets are destroyed
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
        self.filter_vars.clear()
        
        # Reset select all checkbox
        self.select_all_var.set(False)
        
        # Disable refresh button while loading
        self.refresh_btn.configure(state='disabled')
        
        # Show loading message
        loading_label = ttk.Label(self.filters_frame, text="Loading filters...")
        loading_label.pack(pady=10)
        self.filter_frame.update()
        
        try:
            # Get new filters
            filters = self.hotel_scraper.get_filter_details(self.destination.get())
            loading_label.destroy()
            
            if filters and 'all' in filters:
                for filter_item in filters['all']:
                    # Create new variables and widgets
                    var = tk.BooleanVar()
                    var.set(False)  # Explicitly set to False
                    
                    # Create new checkbutton with explicit default state
                    checkbox = ttk.Checkbutton(self.filters_frame, 
                                             text=filter_item['name'],
                                             variable=var,
                                             command=self.update_select_all_state)
                    checkbox.state(['!selected'])  # Explicitly set unchecked state
                    checkbox.pack(anchor="w", padx=10, pady=2)
                    
                    # Store in filter_vars dictionary
                    self.filter_vars[filter_item['name']] = {
                        'var': var,
                        'widget': checkbox
                    }
        except Exception as e:
            loading_label.destroy()
            error_label = ttk.Label(self.filters_frame, 
                                  text="Error loading filters.\nPlease try again.",
                                  foreground="red")
            error_label.pack(pady=10)
            error_label.after(3000, error_label.destroy)  # Remove error message after 3 seconds
        finally:
            # Re-enable refresh button
            self.refresh_btn.configure(state='normal')
            
    def update_select_all_state(self):
        """Update select all checkbox state based on individual checkboxes"""
        if not self.filter_vars:  # If no filters, keep unchecked
            self.select_all_var.set(False)
            return
            
        # Get current search text
        search_text = self.search_var.get().lower()
        
        # Only consider visible checkboxes for the select all state
        visible_checkboxes = [
            items['var'].get() 
            for name, items in self.filter_vars.items() 
            if not search_text or search_text in name.lower()
        ]
        
        if visible_checkboxes:
            all_selected = all(visible_checkboxes)
            self.select_all_var.set(all_selected)
        else:
            self.select_all_var.set(False)
        
    def toggle_all_filters(self):
        """Toggle all filter checkboxes based on select all state"""
        select_all = self.select_all_var.get()
        search_text = self.search_var.get().lower()
        
        for name, items in self.filter_vars.items():
            # Only toggle checkboxes that match the current search
            if not search_text or search_text in name.lower():
                items['var'].set(select_all)
                items['widget'].pack(anchor="w", padx=10, pady=2)
            else:
                # Keep the checkbox state but hide it
                items['widget'].pack_forget()
                
    def filter_search(self, search_text):
        """Filter visible checkboxes based on search text"""
        search_text = search_text.lower()
        visible_matches = False
        
        # First hide all checkboxes
        for items in self.filter_vars.values():
            items['widget'].pack_forget()
        
        # Then show only matching ones
        for name, items in self.filter_vars.items():
            if search_text in name.lower():
                items['widget'].pack(anchor="w", padx=10, pady=2)
                visible_matches = True
        
        # Update select all state based on visible checkboxes
        if visible_matches:
            # Only consider currently visible checkboxes
            visible_states = [
                items['var'].get() 
                for name, items in self.filter_vars.items() 
                if search_text in name.lower()
            ]
            self.select_all_var.set(all(visible_states))
        else:
            self.select_all_var.set(False)
        
    def get_search_params(self):
        selected_filters = [name for name, items in self.filter_vars.items() if items['var'].get()]
        return {
            "destination": self.destination.get(),
            "checkin_date": self.checkin_cal.get_date(),
            "checkout_date": self.checkout_cal.get_date(),
            "adults": self.adults.get(),
            "rooms": self.rooms.get(),
            "children": self.children.get(),
            "search_type": self.search_type.get(),
            "selected_filters": selected_filters
        }
