import tkinter as tk
from tkinter import ttk
import webbrowser

class ResultsFrame:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Search Results", padding="10")
        self.create_results_table()
        
    def create_results_table(self):
        # Create container frame for treeview and scrollbars
        tree_frame = ttk.Frame(self.frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Make the tree frame expand to fill available space
        self.frame.grid_propagate(False)
        self.frame.configure(height=500, width=1200)

        # Create Treeview
        columns = ("serial", "name", "location", "price", "tax", "review", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings
        self.tree.heading("serial", text="#")
        self.tree.heading("name", text="Hotel Name")
        self.tree.heading("location", text="Location")
        self.tree.heading("price", text="Price ▼", command=lambda: self.sort_by_number("price"))
        self.tree.heading("tax", text="Tax ▼", command=lambda: self.sort_by_number("tax"))
        self.tree.heading("review", text="Review")
        self.tree.heading("date", text="Date")
        
        # Store sort states
        self.sort_states = {"price": True, "tax": True}
        
        # Configure columns
        min_width = 120
        self.tree.column("serial", width=50, minwidth=50, stretch=False)
        self.tree.column("name", width=400, minwidth=min_width, stretch=True)
        self.tree.column("location", width=300, minwidth=min_width, stretch=True)
        self.tree.column("price", width=150, minwidth=min_width, stretch=True)
        self.tree.column("tax", width=150, minwidth=min_width, stretch=True)
        self.tree.column("review", width=150, minwidth=min_width, stretch=True)
        self.tree.column("date", width=100, minwidth=min_width, stretch=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid everything
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Copy button
        copy_button = ttk.Button(controls_frame, text="Copy Table Content", command=self.copy_table_content)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Double click handler
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        hotel_data = self.tree.item(item)
        if "values" in hotel_data and hotel_data["values"]:
            link = hotel_data["tags"][0] if hotel_data["tags"] else None
            if link:
                webbrowser.open(link)
                
    def sort_by_number(self, col):
        # Toggle sort state
        self.sort_states[col] = not self.sort_states[col]
        reverse = self.sort_states[col]
        
        # Update header
        arrow = "▼" if reverse else "▲"
        self.tree.heading(col, text=f"{col.title()} {arrow}")
        
        # Sort items
        items = [(self.extract_number(self.tree.set(item, col)), item) 
                for item in self.tree.get_children('')]
        items.sort(reverse=reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
            
    def extract_number(self, value):
        try:
            numeric_str = ''.join(filter(lambda x: x.isdigit() or x == '.', value))
            return float(numeric_str) if numeric_str else 0
        except ValueError:
            return 0
            
    def copy_table_content(self):
        headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        items = [self.tree.item(item_id)["values"] for item_id in self.tree.get_children()]
        
        content = ["\t".join(headers)]
        content.extend("\t".join(str(value) for value in item) for item in items)
        
        final_content = "\n".join(content)
        self.frame.master.clipboard_clear()
        self.frame.master.clipboard_append(final_content)
        
    def update_results(self, hotel_results):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        for hotel in hotel_results:
            price_text = hotel["pricing"].text if hotel["pricing"] else "N/A"
            tax_text = hotel["tax"] if hotel["tax"] else "₹0"
            
            values = (
                hotel.get("serial_no", ""),
                hotel["name"],
                hotel["location"],
                self.format_price(price_text),
                self.format_price(tax_text),
                hotel["review"] if hotel["review"] else "N/A",
                hotel.get("date", "N/A")
            )
            self.tree.insert("", tk.END, values=values, tags=(hotel["link"],))
            
    def format_price(self, price_text):
        if not price_text or price_text == "N/A":
            return "₹0"
        numeric_value = self.extract_number(price_text)
        return f"₹{numeric_value:,.2f}"
