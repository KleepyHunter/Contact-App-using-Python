import sqlite3
from contact import Contact  # Import the Contact class
from utils import special_input, ReturnToMainMenu, ReturnToPreviousStep  # Exceptions for navigation

class ContactManager:
    def __init__(self, db_name="contacts.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create database tables if they don't already exist.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                notes TEXT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            );
        """)
        self.conn.commit()

    def add_contact(self, name, phones=None, emails=None, addresses=None, notes=""):
        """
        Adds a new contact to the database.
        """
        phones = phones or []
        emails = emails or []
        addresses = addresses or []

        # Check for duplicate names
        self.cursor.execute("SELECT id, name FROM contacts WHERE name = ?", (name,))
        result = self.cursor.fetchone()

        if result:
            contact_id = result[0]
            print(f"A contact with the name '{name}' already exists.")
            choice = special_input("Do you want to merge the contacts? (yes/no): ", step="merge_prompt").lower()
            if choice == "yes":
                self.merge_contact(contact_id, phones, emails, addresses, notes)
                print(f"Contact '{name}' merged successfully.")
                return

        # Add new contact
        self.cursor.execute("INSERT INTO contacts (name, notes) VALUES (?, ?)", (name, notes))
        contact_id = self.cursor.lastrowid

        for phone in phones:
            self.cursor.execute("INSERT INTO phones (contact_id, phone) VALUES (?, ?)", (contact_id, phone))
        for email in emails:
            self.cursor.execute("INSERT INTO emails (contact_id, email) VALUES (?, ?)", (contact_id, email))
        for address in addresses:
            self.cursor.execute("INSERT INTO addresses (contact_id, address) VALUES (?, ?)", (contact_id, address))

        self.conn.commit()
        print(f"Contact '{name}' added successfully.")

    def merge_contact(self, contact_id, phones, emails, addresses, notes):
        """
        Merges additional details into an existing contact.
        """
        for phone in phones:
            self.cursor.execute("INSERT OR IGNORE INTO phones (contact_id, phone) VALUES (?, ?)", (contact_id, phone))
        for email in emails:
            self.cursor.execute("INSERT OR IGNORE INTO emails (contact_id, email) VALUES (?, ?)", (contact_id, email))
        for address in addresses:
            self.cursor.execute("INSERT OR IGNORE INTO addresses (contact_id, address) VALUES (?, ?)", (contact_id, address))

        # Append notes
        self.cursor.execute("SELECT notes FROM contacts WHERE id = ?", (contact_id,))
        existing_notes = self.cursor.fetchone()[0]
        updated_notes = f"{existing_notes}\n{notes}" if existing_notes else notes
        self.cursor.execute("UPDATE contacts SET notes = ? WHERE id = ?", (updated_notes, contact_id))
        self.conn.commit()

    def show_all_contacts(self):
        """
        Displays all contacts with their names and phone numbers.
        """
        self.cursor.execute("SELECT id, name FROM contacts")
        contacts = self.cursor.fetchall()
        if not contacts:
            return 0
        for contact_id, name in contacts:
            self.cursor.execute("SELECT phone FROM phones WHERE contact_id = ?", (contact_id,))
            phones = [row[0] for row in self.cursor.fetchall()]
            phone_display = ", ".join(phones) if phones else ""
            print(f"ID: {contact_id}, Name: {name}, Phone(s): {phone_display}")
        return 1

    def inspect_contact(self, contact_id):
        """
        Displays all details of a contact by ID in a formatted, readable manner,
        with options to update, add, or delete specific categories of the record.
        """
        try:
            self.cursor.execute("SELECT name, notes FROM contacts WHERE id = ?", (contact_id,))
            result = self.cursor.fetchone()

            if not result:
                print(f"No contact found with ID {contact_id}.")
                return

            name, notes = result
            self.cursor.execute("SELECT phone FROM phones WHERE contact_id = ?", (contact_id,))
            phones = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT email FROM emails WHERE contact_id = ?", (contact_id,))
            emails = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT address FROM addresses WHERE contact_id = ?", (contact_id,))
            addresses = [row[0] for row in self.cursor.fetchall()]

            while True:
                try:
                    print(f"\nContact Details (ID: {contact_id})")
                    print("=" * 30)
                    print(f"1. Name: {name or 'Unidentified contact'}")
                    print(f"2. Phones: {', '.join(phones) if phones else 'None'}")
                    print(f"3. Emails: {', '.join(emails) if emails else 'None'}")
                    print(f"4. Addresses: {', '.join(addresses) if addresses else 'None'}")
                    print(f"5. Notes: {notes or 'None'}")
                    print("6. Back to Main Menu")
                    print("=" * 30)

                    choice = special_input("Enter the number of the category to manage or '6' to return: ", step="manage_contact")

                    if choice == "1":
                        # Manage Name
                        while True:
                            print("\n1. Update Name")
                            print("2. Back")
                            sub_choice = special_input("Enter your choice: ", step="manage_name")
                            if sub_choice == "1":
                                try:
                                    new_name = special_input("Enter new name: ", step="update_name")
                                    self.cursor.execute("UPDATE contacts SET name = ? WHERE id = ?", (new_name, contact_id))
                                    self.conn.commit()
                                    name = new_name
                                    print("Name updated successfully.")
                                except Exception as e:
                                    print(f"An error occurred while updating the name: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "2":
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif choice == "2":
                        # Manage Phones
                        while True:
                            print("\n1. Add Phone")
                            print("2. Remove Phone")
                            print("3. Back")
                            sub_choice = special_input("Enter your choice: ", step="manage_phones")
                            if sub_choice == "1":
                                try:
                                    new_phone = special_input("Enter new phone: ", step="add_phone")
                                    self.cursor.execute("INSERT INTO phones (contact_id, phone) VALUES (?, ?)", (contact_id, new_phone))
                                    phones.append(new_phone)
                                    self.conn.commit()
                                    print("Phone added successfully.")
                                except Exception as e:
                                    print(f"An error occurred while adding a phone: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "2":
                                try:
                                    if not phones:
                                        print("No phones available to remove.")
                                        continue
                                    print("Current Phones:")
                                    for i, phone in enumerate(phones, start=1):
                                        print(f"{i}. {phone}")
                                    phone_index = int(special_input("Enter the number of the phone to remove: ", step="remove_phone_index")) - 1
                                    if 0 <= phone_index < len(phones):
                                        phone_to_remove = phones[phone_index]
                                        self.cursor.execute("DELETE FROM phones WHERE contact_id = ? AND phone = ?", (contact_id, phone_to_remove))
                                        phones.pop(phone_index)
                                        self.conn.commit()
                                        print("Phone removed successfully.")
                                    else:
                                        print("Invalid selection. Please try again.")
                                except ValueError:
                                    print("Invalid input. Please enter a valid number.")
                                except Exception as e:
                                    print(f"An error occurred while removing the phone: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "3":
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif choice == "3":
                        # Manage Emails
                        while True:
                            print("\n1. Add Email")
                            print("2. Remove Email")
                            print("3. Back")
                            sub_choice = special_input("Enter your choice: ", step="manage_emails")
                            if sub_choice == "1":
                                try:
                                    new_email = special_input("Enter new email: ", step="add_email")
                                    self.cursor.execute("INSERT INTO emails (contact_id, email) VALUES (?, ?)", (contact_id, new_email))
                                    emails.append(new_email)
                                    self.conn.commit()
                                    print("Email added successfully.")
                                except Exception as e:
                                    print(f"An error occurred while adding an email: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "2":
                                try:
                                    if not emails:
                                        print("No emails available to remove.")
                                        continue
                                    print("Current Emails:")
                                    for i, email in enumerate(emails, start=1):
                                        print(f"{i}. {email}")
                                    email_index = int(special_input("Enter the number of the email to remove: ", step="remove_email_index")) - 1
                                    if 0 <= email_index < len(emails):
                                        email_to_remove = emails[email_index]
                                        self.cursor.execute("DELETE FROM emails WHERE contact_id = ? AND email = ?", (contact_id, email_to_remove))
                                        emails.pop(email_index)
                                        self.conn.commit()
                                        print("Email removed successfully.")
                                    else:
                                        print("Invalid selection. Please try again.")
                                except ValueError:
                                    print("Invalid input. Please enter a valid number.")
                                except Exception as e:
                                    print(f"An error occurred while removing the email: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "3":
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif choice == "4":
                        # Manage Addresses
                        while True:
                            print("\n1. Add Address")
                            print("2. Remove Address")
                            print("3. Back")
                            sub_choice = special_input("Enter your choice: ", step="manage_addresses")
                            if sub_choice == "1":
                                try:
                                    new_address = special_input("Enter new address: ", step="add_address")
                                    self.cursor.execute("INSERT INTO addresses (contact_id, address) VALUES (?, ?)", (contact_id, new_address))
                                    addresses.append(new_address)
                                    self.conn.commit()
                                    print("Address added successfully.")
                                except Exception as e:
                                    print(f"An error occurred while adding an address: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "2":
                                try:
                                    if not addresses:
                                        print("No addresses available to remove.")
                                        continue
                                    print("Current Addresses:")
                                    for i, address in enumerate(addresses, start=1):
                                        print(f"{i}. {address}")
                                    address_index = int(special_input("Enter the number of the address to remove: ", step="remove_address_index")) - 1
                                    if 0 <= address_index < len(addresses):
                                        address_to_remove = addresses[address_index]
                                        self.cursor.execute("DELETE FROM addresses WHERE contact_id = ? AND address = ?", (contact_id, address_to_remove))
                                        addresses.pop(address_index)
                                        self.conn.commit()
                                        print("Address removed successfully.")
                                    else:
                                        print("Invalid selection. Please try again.")
                                except ValueError:
                                    print("Invalid input. Please enter a valid number.")
                                except Exception as e:
                                    print(f"An error occurred while removing the address: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "3":
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif choice == "5":
                        # Manage Notes
                        while True:
                            print("\n1. Update Notes")
                            print("2. Back")
                            sub_choice = special_input("Enter your choice: ", step="manage_notes")
                            if sub_choice == "1":
                                try:
                                    new_notes = special_input("Enter new notes: ", step="update_notes")
                                    self.cursor.execute("UPDATE contacts SET notes = ? WHERE id = ?", (new_notes, contact_id))
                                    self.conn.commit()
                                    notes = new_notes
                                    print("Notes updated successfully.")
                                except Exception as e:
                                    print(f"An error occurred while updating notes: {e}")
                                    raise ReturnToPreviousStep
                            elif sub_choice == "2":
                                break
                            else:
                                print("Invalid choice. Please try again.")

                    elif choice == "6":
                        print("Returning to the main menu...")
                        break

                    else:
                        print("Invalid choice. Please try again.")
                except ReturnToPreviousStep:
                    continue
                except ReturnToMainMenu:
                    break

        except Exception as e:
            print(f"An error occurred while managing the contact: {e}")
            raise ReturnToPreviousStep
