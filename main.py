import tkinter as tk
from tkinter import messagebox, simpledialog
from contact_manager import ContactManager

class ContactManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.manager = ContactManager()

        # Search bar and label
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_contacts)  # Trigger search on key release

        # Frame for contact list
        self.frame_list = tk.Frame(self.root)
        self.frame_list.pack(fill=tk.BOTH, expand=True)

        # Contact list
        self.contact_list = tk.Listbox(self.frame_list, height=20, width=50)
        self.contact_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.contact_list.bind("<Double-1>", self.show_contact_details)  # Bind double-click event

        # Scrollbar for contact list
        self.scrollbar = tk.Scrollbar(self.frame_list, orient=tk.VERTICAL, command=self.contact_list.yview)
        self.contact_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for actions
        self.btn_add = tk.Button(self.root, text="Add Contact", command=self.add_contact)
        self.btn_exit = tk.Button(self.root, text="Exit", command=self.root.quit)

        self.btn_add.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_exit.pack(side=tk.RIGHT, padx=10, pady=10)

        # Load contacts on startup
        self.load_contacts()

    def load_contacts(self, search_query=""):
        """Load contacts from the database and display them."""
        self.contact_list.delete(0, tk.END)
        try:
            if search_query:
                self.manager.cursor.execute(
                    "SELECT id, name FROM contacts WHERE name LIKE ?", (f"%{search_query}%",)
                )
            else:
                self.manager.cursor.execute("SELECT id, name FROM contacts")
            contacts = self.manager.cursor.fetchall()
            for contact in contacts:
                self.contact_list.insert(tk.END, f"{contact[0]}: {contact[1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load contacts: {e}")

    def search_contacts(self, event):
        """Search for contacts based on user input."""
        search_query = self.search_entry.get().strip()
        self.root.after(300, lambda: self.load_contacts(search_query))  # Delay search to avoid excessive queries

    def show_contact_details(self, event):
        """Display the details of the selected contact."""
        try:
            selected = self.contact_list.get(self.contact_list.curselection())
            contact_id = int(selected.split(":")[0])

            # Fetch contact details
            self.manager.cursor.execute("SELECT name, notes FROM contacts WHERE id = ?", (contact_id,))
            contact_data = self.manager.cursor.fetchone()
            if not contact_data:
                messagebox.showerror("Error", "Contact not found!")
                return

            name, notes = contact_data
            self.manager.cursor.execute("SELECT phone FROM phones WHERE contact_id = ?", (contact_id,))
            phones = [row[0] for row in self.manager.cursor.fetchall()]
            self.manager.cursor.execute("SELECT email FROM emails WHERE contact_id = ?", (contact_id,))
            emails = [row[0] for row in self.manager.cursor.fetchall()]
            self.manager.cursor.execute("SELECT address FROM addresses WHERE contact_id = ?", (contact_id,))
            addresses = [row[0] for row in self.manager.cursor.fetchall()]

            # Create a new window to display details
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Contact Details - {name}")
            tk.Label(detail_window, text=f"Name: {name}", font=("Arial", 14)).pack(pady=5)
            tk.Label(detail_window, text=f"Phones: {', '.join(phones) or 'None'}").pack(pady=5)
            tk.Label(detail_window, text=f"Emails: {', '.join(emails) or 'None'}").pack(pady=5)
            tk.Label(detail_window, text=f"Addresses: {', '.join(addresses) or 'None'}").pack(pady=5)
            tk.Label(detail_window, text=f"Notes: {notes or 'None'}").pack(pady=5)

            tk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)

        except IndexError:
            messagebox.showwarning("Warning", "No contact selected!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not display contact details: {e}")

    def add_contact(self):
        """Add a new contact."""
        try:
            name = simpledialog.askstring("Input", "Enter name:")
            if not name:
                return
            phone = simpledialog.askstring("Input", "Enter phone (comma-separated):")
            email = simpledialog.askstring("Input", "Enter email (comma-separated):")
            address = simpledialog.askstring("Input", "Enter address (comma-separated):")
            notes = simpledialog.askstring("Input", "Enter notes:")

            phones = phone.split(",") if phone else []
            emails = email.split(",") if email else []
            addresses = address.split(",") if address else []

            self.manager.add_contact(name, phones, emails, addresses, notes)
            messagebox.showinfo("Success", f"Contact '{name}' added successfully!")
            self.load_contacts()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add contact: {e}")

if __name__ == "__main__":
    # Initialize Tkinter root and start the Contact Manager UI
    root = tk.Tk()
    app = ContactManagerUI(root)
    root.mainloop()
