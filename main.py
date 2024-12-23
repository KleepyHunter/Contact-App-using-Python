from contact_manager import ContactManager
from utils import special_input, ReturnToMainMenu, ReturnToPreviousStep

if __name__ == "__main__":
    manager = ContactManager()

    while True:
        try:
            # Display the contact list as the default interface
            print("\n--- Contact List ---")
            try:
                contacts = manager.show_all_contacts()  # Get all contacts
                if not contacts:
                    print("No contacts found. You can add a new contact.")

            except Exception as e:
                print(f"An error occurred while loading the contact list: {e}")
                raise ReturnToMainMenu

            # Show action options
            print("\nActions:")
            print("1. Edit Contact by ID")
            print("2. Add New Contact")
            print("3. Search for a Contact")
            print("4. Exit")

            action_choice = special_input("Enter your choice: ", step="action_menu")

            if action_choice == "1":  # Edit Contact
                try:
                    contact_id = int(special_input("Enter the contact ID to edit: ", step="edit_contact"))
                    manager.inspect_contact(contact_id)  # Enter contact's management interface
                except ValueError:
                    print("Invalid ID. Please enter a valid numeric ID.")
                    raise ReturnToPreviousStep
                except ReturnToPreviousStep:
                    continue

            elif action_choice == "2":  # Add New Contact
                try:
                    name = special_input("Enter name: ", step="add_name")
                    phones = special_input("Enter phone(s) (comma-separated): ", step="add_phones").split(",")
                    emails = special_input("Enter email(s) (comma-separated): ", step="add_emails").split(",")
                    addresses = special_input("Enter address(es) (comma-separated): ", step="add_addresses").split(",")
                    notes = special_input("Enter notes: ", step="add_notes")
                    manager.add_contact(name, phones, emails, addresses, notes)
                except ReturnToPreviousStep:
                    continue

            elif action_choice == "3":  # Search for a Contact
                try:
                    search_category = special_input("Enter category to search (name, phone, email, address, or all): ", step="search_category").lower()
                    search_keyword = special_input("Enter keyword to search: ", step="search_keyword")
                    search_results = manager.search_contact(search_keyword, search_category)
                    if search_results:
                        print("\nSearch Results:")
                        for contact in search_results:
                            print(f"ID: {contact[0]}, Name: {contact[1] or 'Unidentified contact'}, Phones: {contact[2] or 'None'}")
                    else:
                        print("No matching contacts found.")
                except ReturnToPreviousStep:
                    continue

            elif action_choice == "4":  # Exit
                print("Exiting Contact Manager. Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

        except ReturnToMainMenu:
            continue  # Restart the main interface
