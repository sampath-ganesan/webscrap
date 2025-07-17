import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

class SearchFrame:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Search Criteria", padding="10")
        
        # Location
        ttk.Label(self.frame, text="Destination:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.destination = ttk.Entry(self.frame, width=40)
        self.destination.insert(0, "Chennai, India")
        self.destination.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Check-in date
        ttk.Label(self.frame, text="Check-in Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.checkin_cal = Calendar(self.frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.checkin_cal.grid(row=1, column=1, columnspan=2, pady=5)
        
        # Check-out date
        ttk.Label(self.frame, text="Check-out Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.checkout_cal = Calendar(self.frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.checkout_cal.grid(row=2, column=1, columnspan=2, pady=5)
        
        # Adults
        ttk.Label(self.frame, text="Adults:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.adults = ttk.Spinbox(self.frame, from_=1, to=10, width=5)
        self.adults.set(2)
        self.adults.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Rooms
        ttk.Label(self.frame, text="Rooms:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rooms = ttk.Spinbox(self.frame, from_=1, to=5, width=5)
        self.rooms.set(1)
        self.rooms.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Children
        ttk.Label(self.frame, text="Children:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.children = ttk.Spinbox(self.frame, from_=0, to=5, width=5)
        self.children.set(0)
        self.children.grid(row=5, column=1, sticky=tk.W, pady=5)

        # Search Type
        ttk.Label(self.frame, text="Search Type:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.search_type = tk.StringVar(value="single")
        ttk.Radiobutton(self.frame, text="Single Day", variable=self.search_type, 
                       value="single").grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(self.frame, text="Date Range", variable=self.search_type, 
                       value="range").grid(row=6, column=2, sticky=tk.W, pady=5)
        
    def get_search_params(self):
        return {
            "destination": self.destination.get(),
            "checkin_date": self.checkin_cal.get_date(),
            "checkout_date": self.checkout_cal.get_date(),
            "adults": self.adults.get(),
            "rooms": self.rooms.get(),
            "children": self.children.get(),
            "search_type": self.search_type.get()
        }
