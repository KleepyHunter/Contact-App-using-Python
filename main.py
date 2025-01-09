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
            detail_window.geometry("500x400")  # Fixed size
            detail_window.resizable(False, False)

            fields = [
                ("Name", name),
                ("Phones", ", ".join(phones) if phones else "None"),
                ("Emails", ", ".join(emails) if emails else "None"),
                ("Addresses", ", ".join(addresses) if addresses else "None"),
                ("Notes", notes or "None")
            ]

            for idx, (field_name, field_value) in enumerate(fields):
                frame = tk.Frame(detail_window)
                frame.pack(fill=tk.X, pady=5, padx=10)

                # Field label
                label = tk.Label(frame, text=f"{field_name}:", anchor="w", width=12)
                label.pack(side=tk.LEFT)

                # Field content
                text_box = tk.Text(frame, height=2, width=30, wrap=tk.WORD)
                text_box.insert(tk.END, field_value)
                text_box.configure(state="disabled")  # Make it read-only
                text_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

                # Edit button
                edit_button = tk.Button(frame, text="Edit", command=lambda fn=field_name, fv=field_value: self.edit_field(contact_id, fn, fv))
                edit_button.pack(side=tk.RIGHT, padx=5)

            # Close button
            tk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)

        except IndexError:
            messagebox.showwarning("Warning", "No contact selected!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not display contact details: {e}")

    def edit_field(self, contact_id, field_name, current_value):
        """Edit a specific field of a contact."""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit {field_name}")
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)

        tk.Label(edit_window, text=f"Current {field_name}:").pack(pady=10)
        current_value_label = tk.Label(edit_window, text=current_value, wraplength=350, justify="left", relief="sunken")
        current_value_label.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(edit_window, text=f"New {field_name}:").pack(pady=10)
        new_value_entry = tk.Entry(edit_window, width=50)
        new_value_entry.pack(padx=10, pady=5)

        def save_changes():
            new_value = new_value_entry.get().strip()
            if not new_value:
                messagebox.showwarning("Warning", f"New {field_name} cannot be empty!")
                return

            # Update the database
            try:
                if field_name == "Name":
                    self.manager.cursor.execute("UPDATE contacts SET name = ? WHERE id = ?", (new_value, contact_id))
                elif field_name == "Phones":
                    self.manager.cursor.execute("INSERT INTO phones (contact_id, phone) VALUES (?, ?)", (contact_id, new_value))
                elif field_name == "Emails":
                    self.manager.cursor.execute("INSERT INTO emails (contact_id, email) VALUES (?, ?)", (contact_id, new_value))
                elif field_name == "Addresses":
                    self.manager.cursor.execute("INSERT INTO addresses (contact_id, address) VALUES (?, ?)", (contact_id, new_value))
                elif field_name == "Notes":
                    self.manager.cursor.execute("UPDATE contacts SET notes = ? WHERE id = ?", (new_value, contact_id))
                self.manager.conn.commit()
                messagebox.showinfo("Success", f"{field_name} updated successfully!")
                edit_window.destroy()
                self.load_contacts()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update {field_name}: {e}")

        tk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
        tk.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=10)

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
