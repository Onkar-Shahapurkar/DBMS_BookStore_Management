import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import csv
from tkinter.filedialog import asksaveasfilename
from tkcalendar import Calendar, DateEntry
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

db = mysql.connector.connect(
            host="localhost",
            user="root",    # Replace with your database username
            password="onkar2814",  # Replace with your database password
            database="DBMS"  # Replace with your database name
        )
cursor = db.cursor()

class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookstore Management System")

        # Connect to the database
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",    # Replace with your database username
            password="onkar2814",  # Replace with your database password
            database="DBMS"  # Replace with your database name
        )
        self.cursor = self.db.cursor()

        # Create GUI components
        self.create_widgets()

        self.add_order_button = tk.Button(root, text="Place Order", command=self.place_order)
        self.add_order_button.pack(pady=5)

        self.generate_report_button = tk.Button(root, text="Generate Sales Report", command=self.generate_report)
        self.generate_report_button.pack(pady=5)

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        # Title label
        title_label = tk.Label(main_frame, text="Bookstore Management System", font=("Arial", 24))
        title_label.pack(pady=10)

        # Add book frame
        add_book_frame = tk.LabelFrame(main_frame, text="Add New Book", padx=10, pady=10)
        add_book_frame.pack(pady=10)

        self.isbn_entry = self.create_label_entry(add_book_frame, "ISBN:", 0)
        self.title_entry = self.create_label_entry(add_book_frame, "Title:", 1)
        self.author_entry = self.create_label_entry(add_book_frame, "Author:", 2)

        self.genre_entry = tk.StringVar(value="Select Genre")
        self.create_genre_dropdown(add_book_frame, "Genre:", 3)

        self.price_entry = self.create_label_entry(add_book_frame, "Price:", 4)
        self.stock_entry = self.create_label_entry(add_book_frame, "Stock:", 5)

        validate_isbn = self.root.register(self.validate_isbn_input)
        self.isbn_entry.config(validate="key", validatecommand=(validate_isbn, "%P"))
        validate_author = self.root.register(self.validate_author_input)
        self.author_entry.config(validate="key", validatecommand=(validate_author, "%P"))
        validate_price = self.root.register(self.validate_price_input)
        self.price_entry.config(validate="key", validatecommand=(validate_price, "%P"))
        validate_stock = self.root.register(self.validate_stock_input)
        self.stock_entry.config(validate="key", validatecommand=(validate_stock, "%P"))

        submit_button = tk.Button(add_book_frame, text="Add Book", command=self.submit_book)
        submit_button.grid(row=6, columnspan=2, pady=10)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        view_books_button = tk.Button(button_frame, text="View All Books", command=self.view_books)
        view_books_button.pack(side=tk.LEFT, padx=5)

        view_audit_logs_button = tk.Button(button_frame, text="View Audit Logs", command=self.view_audit_logs)
        view_audit_logs_button.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(button_frame, text="Search Book", command=self.search_book)
        search_button.pack(side=tk.LEFT, padx=5)

        manage_customers_button = tk.Button(button_frame, text="Add Customers", command=self.manage_customers)
        manage_customers_button.pack(side=tk.LEFT, padx=5)

        customer_orders_button = tk.Button(button_frame, text="View Customer Orders", command=self.view_customer_orders)
        customer_orders_button.pack(side=tk.LEFT, padx=5)

        manage_borrowing_button = tk.Button(button_frame, text="Manage Borrowing", command=self.manage_borrowing)
        manage_borrowing_button.pack(side=tk.LEFT, padx=5)

        manage_payment_button = tk.Button(button_frame, text="Manage Payments", command=self.manage_payments)
        manage_payment_button.pack(side=tk.LEFT, padx=5)

        manage_suppliers_button = tk.Button(button_frame, text="Manage Suppliers", command=self.manage_suppliers)
        manage_suppliers_button.pack(side=tk.LEFT, padx=5)

        manage_shipments_button = tk.Button(button_frame, text="Manage Shipments", command=self.manage_shipments)
        manage_shipments_button.pack(side=tk.LEFT, padx=5)

        # Book List Frame
        self.book_list_frame = tk.LabelFrame(main_frame, text="Books", padx=10, pady=10)
        self.book_list_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.book_list_frame, columns=("ISBN", "Title", "Author", "Genre", "Price", "Stock"), show='headings')
        self.tree.heading("ISBN", text="ISBN")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Stock", text="Stock")

        self.tree.pack(padx=10, pady=10)

        # Bind treeview select event
        self.tree.bind("<Double-1>", self.load_selected_book)

    def create_label_entry(self, parent, label_text, row):
        """Helper function to create a label and entry widget."""
        tk.Label(parent, text=label_text).grid(row=row, column=0)
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1)
        return entry

    def validate_isbn_input(self, input_value):
        if input_value.isdigit() or input_value == "":
            if len(input_value) <= 13:
                return True
            else:
                messagebox.showwarning("Validation Error", "ISBN cannot exceed 13 digits.")
                return False
        else:
            messagebox.showwarning("Validation Error", "ISBN must contain only digits.")
            return False

    def validate_author_input(self, input_value):
        if all(char.isalpha() or char in " .-" for char in input_value) or input_value == "":
            if len(input_value) <= 50:  # Optional: Limit author name length
                return True
            else:
                messagebox.showwarning("Validation Error", "Author name cannot exceed 50 characters.")
                return False
        else:
            messagebox.showwarning("Validation Error",
                                   "Author name can only contain letters, spaces, and basic punctuation.")
            return False

    def validate_price_input(self, input_value):
        try:
            # Allow empty input
            if input_value == "":
                return True
            # Convert to float to validate numeric value
            value = float(input_value)
            # Ensure the value is non-negative
            if value < 0:
                messagebox.showwarning("Validation Error", "Price cannot be negative.")
                return False
            return True
        except ValueError:
            messagebox.showwarning("Validation Error", "Price must be a valid number.")
            return False

    def validate_stock_input(self, input_value):
        if input_value == "":  # Allow empty input
            return True
        if input_value.isdigit():  # Check if input is numeric
            return True
        else:
            messagebox.showwarning("Validation Error", "Stock must be a non-negative integer.")
            return False

    def create_genre_dropdown(self, parent, label_text, row):
        """Creates a labeled dropdown menu."""
        label = tk.Label(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)

        genres = [
            "Action and Adventure", "Fantasy", "Science Fiction (Sci-Fi)", "Mystery",
            "Horror", "Romance", "Historical Fiction", "Thriller and Suspense",
            "Drama", "Literary Fiction", "Dystopian", "Humor and Satire",
            "Biography and Autobiography", "Self-Help", "History", "Travel",
            "Science and Technology", "Health and Fitness", "Philosophy and Spirituality",
            "True Crime", "Memoir", "Business and Economics"
        ]

        dropdown = ttk.OptionMenu(parent, self.genre_entry, *genres)
        dropdown.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)

    def get_selected_genre(self):
        """Retrieve the selected genre."""
        return self.genre_entry.get()


    def submit_book(self):
        isbn = self.isbn_entry.get()
        title = self.title_entry.get()
        author = self.author_entry.get()
        genre = self.genre_entry.get()
        price = self.price_entry.get()
        stock = self.stock_entry.get()

        try:
            # Validate input
            if not all([isbn, title, author, genre, price, stock]):
                raise ValueError("All fields must be filled!")

            # Insert new book into the database
            self.cursor.execute("""
                INSERT INTO Books (ISBN, Title, Author, Genre, Price, Stock) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (isbn, title, author, genre, float(price), int(stock))
            )
            self.db.commit()
            messagebox.showinfo("Success", "Book added successfully!")

            # Log the addition to the AuditLog
            self.log_audit(f"Added book: {title}")

            # Clear the entries
            self.clear_entries()

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))

    def clear_entries(self):
        """Clear the input fields."""
        self.isbn_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

    def view_books(self):
        # Clear existing data in the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Execute the SQL query to retrieve all books
        self.cursor.execute("SELECT * FROM Books")
        rows = self.cursor.fetchall()

        # Insert the data into the treeview
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_selected_book(self, event):
        """Load selected book data into the entry fields for editing."""
        selected_item = self.tree.selection()[0]
        selected_book = self.tree.item(selected_item)['values']
        self.isbn_entry.delete(0, tk.END)
        self.isbn_entry.insert(0, selected_book[0])
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, selected_book[1])
        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, selected_book[2])
        self.genre_entry.delete(0, tk.END)
        self.genre_entry.insert(0, selected_book[3])
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, selected_book[4])
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, selected_book[5])

        # Add a button to update the selected book
        update_button = tk.Button(self.book_list_frame, text="Update Book", command=self.update_book)
        update_button.pack(pady=10)

        # Add a button to delete the selected book
        delete_button = tk.Button(self.book_list_frame, text="Delete Book", command=self.delete_book)
        delete_button.pack(pady=5)

    def update_book(self):
        isbn = self.isbn_entry.get()
        title = self.title_entry.get()
        author = self.author_entry.get()
        genre = self.genre_entry.get()
        price = self.price_entry.get()
        stock = self.stock_entry.get()

        try:
            # Validate input
            if not all([isbn, title, author, genre, price, stock]):
                raise ValueError("All fields must be filled!")

            # Update book in the database
            self.cursor.execute("""
                UPDATE Books 
                SET Title=%s, Author=%s, Genre=%s, Price=%s, Stock=%s 
                WHERE ISBN=%s""",
                (title, author, genre, float(price), int(stock), isbn)
            )
            self.db.commit()
            messagebox.showinfo("Success", "Book updated successfully!")

            # Log the update to the AuditLog
            self.log_audit(f"Updated book: {title}")

            # Clear the entries
            self.clear_entries()

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))

    def delete_book(self):
        selected_item = self.tree.selection()[0]
        selected_book = self.tree.item(selected_item)['values']
        isbn = selected_book[0]
        title = selected_book[1]

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?"):
            try:
                # Delete book from the database
                self.cursor.execute("DELETE FROM Books WHERE ISBN = %s", (isbn,))
                self.db.commit()
                messagebox.showinfo("Success", "Book deleted successfully!")

                # Log the deletion to the AuditLog
                self.log_audit(f"Deleted book: {title}")

                # Refresh the book list
                self.view_books()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database Error: {err}")

    def search_book(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Book")

        tk.Label(search_window, text="Enter ISBN or Title:").grid(row=0, column=0)
        search_entry = tk.Entry(search_window)
        search_entry.grid(row=0, column=1)

        search_button = tk.Button(search_window, text="Search", command=lambda: self.perform_search(search_entry.get(), search_window))
        search_button.grid(row=1, columnspan=2, pady=10)

    def perform_search(self, query, window):
        # Clear existing data in the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Execute the SQL query to search for books
        self.cursor.execute("SELECT * FROM Books WHERE ISBN = %s OR Title LIKE %s", (query, '%' + query + '%'))
        rows = self.cursor.fetchall()

        # Insert the data into the treeview
        for row in rows:
            self.tree.insert("", tk.END, values=row)

        window.destroy()

    def view_audit_logs(self):
        # Function to retrieve and display audit logs filtered by date range
        def filter_logs_by_date():
            # Get the selected start and end dates from the date entries
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()

            # Convert dates to string format (for SQL query compatibility)
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')

            # Execute the SQL query to retrieve filtered audit logs by date range
            query = """
            SELECT * FROM AuditLog 
            WHERE ActionDate BETWEEN %s AND %s
            ORDER BY ActionDate DESC
            """
            self.cursor.execute(query, (start_date_str, end_date_str))
            rows = self.cursor.fetchall()

            # Clear the existing rows in the Treeview
            for item in tree.get_children():
                tree.delete(item)

            # Insert the filtered rows into the Treeview widget
            for row in rows:
                tree.insert("", tk.END, values=row)

        # Function to generate and download the audit logs as a PDF in table format
        def download_pdf():
            # Fetch all audit logs from the database
            self.cursor.execute("SELECT * FROM AuditLog ORDER BY ActionDate DESC")
            rows = self.cursor.fetchall()

            if rows:
                # Create PDF file to save the audit logs
                filename = f"AuditLogs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                c = canvas.Canvas(filename, pagesize=letter)
                c.setFont("Helvetica", 8)

                # Add title
                c.drawString(200, 750, "Audit Logs")

                # Table headers
                headers = ["Audit ID", "Action", "Table Name", "Action Date", "Details"]
                x_position = 50
                y_position = 730

                # Draw table headers
                for header in headers:
                    c.drawString(x_position, y_position, header)
                    x_position += 100  # Space between columns

                # Draw the data rows
                y_position -= 20  # Move down to the next line
                for row in rows:
                    x_position = 50
                    for item in row:
                        c.drawString(x_position, y_position, str(item))  # Convert each field to string
                        x_position += 100  # Space between columns
                    y_position -= 15  # Move down to the next row

                # Save the PDF
                c.save()

                # Notify user that the PDF has been saved
                print(f"PDF saved as {filename}")

                # Optionally, open the file or provide a download link
                os.startfile(filename)  # For Windows, open the PDF automatically (cross-platform approach may vary)

        # Create a new top-level window to display the audit logs
        audit_window = tk.Toplevel(self.root)
        audit_window.title("Audit Logs")

        # Create a frame for date range selection
        date_frame = tk.Frame(audit_window)
        date_frame.pack(pady=10)

        # Start Date Entry
        tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        start_date_entry = DateEntry(date_frame, date_pattern='yyyy-mm-dd', width=12)
        start_date_entry.grid(row=0, column=1, padx=5)

        # End Date Entry
        tk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5)
        end_date_entry = DateEntry(date_frame, date_pattern='yyyy-mm-dd', width=12)
        end_date_entry.grid(row=0, column=3, padx=5)

        # Search Button
        search_button = tk.Button(date_frame, text="Search", command=filter_logs_by_date)
        search_button.grid(row=0, column=4, padx=10)

        # Create a Treeview widget to display data in a tabular format
        tree = ttk.Treeview(audit_window, columns=("AuditID", "Action", "TableName", "ActionDate", "Details"),
                            show="headings")

        # Define the headings for the columns
        tree.heading("AuditID", text="Audit ID")
        tree.heading("Action", text="Action")
        tree.heading("TableName", text="Table Name")
        tree.heading("ActionDate", text="Action Date")
        tree.heading("Details", text="Details")

        # Set the column widths
        tree.column("AuditID", width=80)
        tree.column("Action", width=150)
        tree.column("TableName", width=150)
        tree.column("ActionDate", width=150)
        tree.column("Details", width=250)

        # Insert rows into the Treeview widget (initially all logs)
        self.cursor.execute("SELECT * FROM AuditLog ORDER BY ActionDate DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        # Add the Treeview to the window
        tree.pack(fill=tk.BOTH, expand=True)

        # Add a vertical scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(audit_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a horizontal scrollbar to the Treeview
        hscrollbar = ttk.Scrollbar(audit_window, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hscrollbar.set)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add a button to download the audit logs as PDF in table format
        download_button = tk.Button(audit_window, text="Download Audit Logs as PDF", command=download_pdf)
        download_button.pack(pady=10)

    def log_audit(self, action):
        # Log actions in the AuditLog table
        self.cursor.execute("INSERT INTO AuditLog (Action, ActionDate) VALUES (%s, NOW())", (action,))
        self.db.commit()

    def place_order(self):
        order_window = tk.Toplevel(self.root)
        order_window.title("Place Order")

        customer_id_label = tk.Label(order_window, text="Customer ID")
        customer_id_label.pack()
        customer_id_entry = tk.Entry(order_window)
        customer_id_entry.pack()

        isbn_label = tk.Label(order_window, text="Book ISBN")
        isbn_label.pack()
        isbn_entry = tk.Entry(order_window)
        isbn_entry.pack()

        quantity_label = tk.Label(order_window, text="Quantity")
        quantity_label.pack()
        quantity_entry = tk.Entry(order_window)
        quantity_entry.pack()

        def save_order():
            try:
                # Get book price
                cursor.execute("SELECT Price FROM Books WHERE ISBN = %s", (isbn_entry.get(),))
                price = cursor.fetchone()[0]

                # Insert into Orderfs and OrderDetails
                cursor.execute("INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES (%s, NOW(), %s)",
                               (int(customer_id_entry.get()), price * int(quantity_entry.get())))
                order_id = cursor.lastrowid

                cursor.execute("INSERT INTO OrderDetails (OrderID, ISBN, Quantity, Price) VALUES (%s, %s, %s, %s)",
                               (order_id, isbn_entry.get(), int(quantity_entry.get()), price))
                db.commit()
                messagebox.showinfo("Success", "Order placed successfully")
                order_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                db.rollback()

        place_order_button = tk.Button(order_window, text="Place Order", command=save_order)
        place_order_button.pack(pady=10)

        # Function to view customer orders

    def view_customer_orders(self):
        self.cursor.execute("SELECT CustomerID, Name, TotalOrders, TotalSpent FROM CustomerOrdersSummary")
        rows = self.cursor.fetchall()

        # Create a new window for displaying customer orders
        order_window = tk.Toplevel(self.root)
        order_window.title("Customer Orders Summary")

        # Create a treeview to display the order details in a table format
        columns = ("CustomerID", "Name", "TotalOrders", "TotalSpent")
        tree = ttk.Treeview(order_window, columns=columns, show='headings')

        # Define the column headers
        tree.heading("CustomerID", text="Customer ID")
        tree.heading("Name", text="Customer Name")
        tree.heading("TotalOrders", text="Total Orders")
        tree.heading("TotalSpent", text="Total Spent")

        # Set the column widths
        tree.column("CustomerID", width=100)
        tree.column("Name", width=150)
        tree.column("TotalOrders", width=100)
        tree.column("TotalSpent", width=100)

        # Insert the rows into the treeview
        for row in rows:
            tree.insert("", tk.END, values=row)

        # Pack the treeview into the window
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def fetch_sales_data(self):
        """Fetch sales data by joining orders, orderdetails, payments, shipments, and salesbygenreauthor."""
        query = """
        SELECT o.OrderID, o.OrderDate, o.TotalAmount, p.PaymentDate, p.Amount AS PaymentAmount,
               s.ShipmentDate, s.DeliveryDate, s.Status AS ShipmentStatus,
               od.ISBN, od.Quantity, od.Price, b.Title, b.Author, b.Genre
        FROM orders o
        JOIN orderdetails od ON o.OrderID = od.OrderID
        JOIN books b ON od.ISBN = b.ISBN
        LEFT JOIN payments p ON o.OrderID = p.OrderID
        LEFT JOIN shipments s ON o.OrderID = s.OrderID
        ORDER BY o.OrderDate DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def generate_report(self):
        """Generate and download the sales report as a CSV file."""
        try:
            sales_data = self.fetch_sales_data()

            if not sales_data:
                messagebox.showerror("No Data", "No sales data available for the report.")
                return

            # Ask for file name and location to save the report
            file_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return  # User canceled the file dialog

            # Write data to CSV file
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "OrderID", "OrderDate", "TotalAmount", "PaymentDate", "PaymentAmount",
                    "ShipmentDate", "DeliveryDate", "ShipmentStatus", "ISBN", "Quantity",
                    "Price", "BookTitle", "BookAuthor", "BookGenre"
                ])  # Write header

                # Write sales data rows
                for row in sales_data:
                    writer.writerow(row)

            messagebox.showinfo("Success", f"Sales report has been successfully generated and saved to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the report: {e}")

    def manage_customers(self):
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Manage Customers")

        # Form fields for customer details
        tk.Label(manage_window, text="Name:").grid(row=0, column=0)
        name_entry = tk.Entry(manage_window)
        name_entry.grid(row=0, column=1)

        tk.Label(manage_window, text="Email:").grid(row=1, column=0)
        email_entry = tk.Entry(manage_window)
        email_entry.grid(row=1, column=1)

        tk.Label(manage_window, text="Phone:").grid(row=2, column=0)
        phone_entry = tk.Entry(manage_window)
        phone_entry.grid(row=2, column=1)

        # Button to add a new customer
        def add_customer():
            name = name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()

            try:
                # Insert customer into the database without specifying CustomerID
                self.cursor.execute("""
                    INSERT INTO Customers (Name, Email, Phone) 
                    VALUES (%s, %s, %s)""", (name, email, phone))
                self.db.commit()
                messagebox.showinfo("Success", "Customer added successfully!")

                # Clear form fields
                name_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)

            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database Error: {err}")

        add_customer_button = tk.Button(manage_window, text="Add Customer", command=add_customer)
        add_customer_button.grid(row=3, columnspan=2, pady=10)

    def manage_shipments(self):
        shipment_window = tk.Toplevel(self.root)
        shipment_window.title("Manage Shipments")

        # Fields for shipments
        tk.Label(shipment_window, text="Order ID").grid(row=0, column=0)
        order_id_entry = tk.Entry(shipment_window)
        order_id_entry.grid(row=0, column=1)

        tk.Label(shipment_window, text="Status").grid(row=1, column=0)
        status_entry = tk.Entry(shipment_window)
        status_entry.grid(row=1, column=1)

        add_shipment_button = tk.Button(shipment_window, text="Add Shipment",
                                        command=lambda: self.add_shipment(order_id_entry.get(), status_entry.get()))
        add_shipment_button.grid(row=2, column=1)

    def add_shipment(self, order_id, status):
        try:
            # Insert into shipments table
            self.cursor.execute("INSERT INTO Shipments (OrderID, ShipmentDate, Status) VALUES (%s, NOW(), %s)",
                                (order_id, status))
            self.db.commit()
            messagebox.showinfo("Success", "Shipment added successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def manage_suppliers(self):
        supplier_window = tk.Toplevel(self.root)
        supplier_window.title("Manage Suppliers")

        # Fields for suppliers
        tk.Label(supplier_window, text="Supplier Name").grid(row=0, column=0)
        supplier_name_entry = tk.Entry(supplier_window)
        supplier_name_entry.grid(row=0, column=1)

        tk.Label(supplier_window, text="Contact").grid(row=1, column=0)
        contact_entry = tk.Entry(supplier_window)
        contact_entry.grid(row=1, column=1)

        tk.Label(supplier_window, text="Address").grid(row=2, column=0)
        address_entry = tk.Entry(supplier_window)
        address_entry.grid(row=2, column=1)

        add_supplier_button = tk.Button(supplier_window, text="Add Supplier",
                                        command=lambda: self.add_supplier(supplier_name_entry.get(),
                                                                          contact_entry.get(), address_entry.get()))
        add_supplier_button.grid(row=3, column=1)

    def add_supplier(self, name, contact, address):
        try:
            # Insert into suppliers table
            self.cursor.execute("INSERT INTO Suppliers (Name, Contact, Address) VALUES (%s, %s, %s)",
                                (name, contact, address))
            self.db.commit()
            messagebox.showinfo("Success", "Supplier added successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def manage_payments(self):
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Manage Payments")

        # Fields for payment
        tk.Label(payment_window, text="Order ID").grid(row=0, column=0)
        order_id_entry = tk.Entry(payment_window)
        order_id_entry.grid(row=0, column=1)

        tk.Label(payment_window, text="Amount").grid(row=1, column=0)
        amount_entry = tk.Entry(payment_window)
        amount_entry.grid(row=1, column=1)

        tk.Label(payment_window, text="Payment Method").grid(row=2, column=0)
        payment_method_entry = tk.Entry(payment_window)
        payment_method_entry.grid(row=2, column=1)

        payment_button = tk.Button(payment_window, text="Add Payment",
                                   command=lambda: self.add_payment(order_id_entry.get(), amount_entry.get(),
                                                                    payment_method_entry.get()))
        payment_button.grid(row=3, column=1)

    def add_payment(self, order_id, amount, method):
        try:
            # Insert into payments table
            self.cursor.execute(
                "INSERT INTO Payments (OrderID, PaymentDate, Amount, PaymentMethod) VALUES (%s, NOW(), %s, %s)",
                (order_id, amount, method))
            self.db.commit()
            messagebox.showinfo("Success", "Payment added successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def manage_borrowing(self):
        borrow_window = tk.Toplevel(self.root)
        borrow_window.title("Manage Borrowing")

        # Fields for borrowing
        tk.Label(borrow_window, text="Customer ID").grid(row=0, column=0)
        customer_id_entry = tk.Entry(borrow_window)
        customer_id_entry.grid(row=0, column=1)

        tk.Label(borrow_window, text="ISBN").grid(row=1, column=0)
        isbn_entry = tk.Entry(borrow_window)
        isbn_entry.grid(row=1, column=1)

        # Custom Date Picker in a single cell with restrictions on date selection
        tk.Label(borrow_window, text="Due Date (YYYY-MM-DD)").grid(row=2, column=0)

        due_date_picker = DateEntry(borrow_window,
                                    date_pattern="yyyy-mm-dd",
                                    width=12,
                                    background="lightblue",
                                    foreground="black",
                                    borderwidth=2,
                                    mindate=date.today())  # Restricts to current or future dates only
        due_date_picker.grid(row=2, column=1)

        borrow_button = tk.Button(borrow_window, text="Borrow Book",
                                  command=lambda: self.borrow_book(customer_id_entry.get(), isbn_entry.get(),
                                                                   due_date_picker.get_date()))
        borrow_button.grid(row=3, column=1)

    def borrow_book(self, customer_id, isbn, due_date):
        try:
            # Insert into borrowing table
            self.cursor.execute(
                "INSERT INTO Borrowing (CustomerID, ISBN, DateBorrowed, DueDate) VALUES (%s, %s, CURDATE(), %s)",
                (customer_id, isbn, due_date))
            self.db.commit()
            messagebox.showinfo("Success", "Book borrowed successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")


# Create the root window
if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()
