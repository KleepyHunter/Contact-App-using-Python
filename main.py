from contact_manager import ContactManager

def main():
    manager = ContactManager()

    while True:
        try:
            print("\n--- Contact Manager ---")
            print("1. Add Contact\n2. View Contacts\n3. Search Contact\n4. Update Contact\n5. Delete Contact\n6. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                name = input("Name: ")
                phone = input("Phone: ")
                email = input("Email: ")
                address = input("Address: ")
                manager.add_contact(name, phone, email, address)

            elif choice == "2":
                contacts = manager.view_contacts()
                for contact in contacts:
                    print(f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")

            elif choice == "3":
                print("Search categories: name, phone, email, address, or all (default)")
                category = input("Enter category to search in: ").lower()
                keyword = input("Enter keyword to search (leave blank to show all): ")
                results = manager.search_contact(keyword, category)
                if results:
                    for contact in results:
                        print(f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")
                else:
                    print("No contacts found.")

            elif choice == "4":
                print("Search categories: name, phone, email, address, or all (default)")
                category = input("Enter category to search in: ").lower()
                keyword = input("Enter keyword to find contacts to update (leave blank to show all): ")
                results = manager.search_contact(keyword, category)
                if results:
                    print("Matching contacts:")
                    for contact in results:
                        print(f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, Address: {contact[4]}")
                    
                    contact_id = int(input("Enter the ID of the contact to update: "))
                    update_category = input("Enter the category to update (name, phone, email, address): ").lower()
                    new_value = input(f"Enter the new value for {update_category}: ")
                    manager.update_contact(contact_id, update_category, new_value)
                else:
                    print("No contacts found matching the keyword.")

            elif choice == "5":
                contact_id = int(input("Enter the ID of the contact to delete: "))
                manager.delete_contact(contact_id)

            elif choice == "6":
                manager.close()
                print("Exiting Contact Manager. Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
