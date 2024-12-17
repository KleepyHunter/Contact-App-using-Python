import sqlite3

class ContactManager:
    def __init__(self, db_name="contacts.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def create_table(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT
            )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")

    def add_contact(self, name, phone, email, address):
        try:
            self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                                (name, phone, email, address))
            self.conn.commit()
            print("Contact added successfully.")
        except Exception as e:
            print(f"Error adding contact: {e}")

    def view_contacts(self):
        try:
            self.cursor.execute("SELECT * FROM contacts")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving contacts: {e}")
            return []

    def search_contact(self, keyword, category="all"):
        try:
            keyword = keyword.strip()
            if not keyword:  # If keyword is blank, return all records
                self.cursor.execute("SELECT * FROM contacts")
            elif category == "name":
                self.cursor.execute("SELECT * FROM contacts WHERE name LIKE ?", (f"%{keyword}%",))
            elif category == "phone":
                self.cursor.execute("SELECT * FROM contacts WHERE phone LIKE ?", (f"%{keyword}%",))
            elif category == "email":
                self.cursor.execute("SELECT * FROM contacts WHERE email LIKE ?", (f"%{keyword}%",))
            elif category == "address":
                self.cursor.execute("SELECT * FROM contacts WHERE address LIKE ?", (f"%{keyword}%",))
            else:
                self.cursor.execute("""
                    SELECT * FROM contacts WHERE 
                    name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error searching contacts: {e}")
            return []

    def show_contact_by_id(self, contact_id):
        try:
            self.cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error retrieving contact by ID: {e}")
            return None

    def update_contact(self, contact_id, category, new_value):
        try:
            # Show the contact that will be updated
            contact = self.show_contact_by_id(contact_id)
            if contact:
                print(f"Contact to be updated: ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")
                
                # Update based on the category
                if category == "name":
                    self.cursor.execute("UPDATE contacts SET name = ? WHERE id = ?", (new_value, contact_id))
                elif category == "phone":
                    self.cursor.execute("UPDATE contacts SET phone = ? WHERE id = ?", (new_value, contact_id))
                elif category == "email":
                    self.cursor.execute("UPDATE contacts SET email = ? WHERE id = ?", (new_value, contact_id))
                elif category == "address":
                    self.cursor.execute("UPDATE contacts SET address = ? WHERE id = ?", (new_value, contact_id))
                else:
                    print("Invalid category. Please choose from name, phone, email, or address.")
                    return
                
                self.conn.commit()
                print("Contact updated successfully.")
            else:
                print("Contact not found.")
        except Exception as e:
            print(f"Error updating contact: {e}")

    def delete_contact(self, contact_id):
        try:
            self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            self.conn.commit()
            print("Contact deleted successfully.")
        except Exception as e:
            print(f"Error deleting contact: {e}")

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            print(f"Error closing the database connection: {e}")
