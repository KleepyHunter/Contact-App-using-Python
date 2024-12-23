class Contact:
    def __init__(self, id, name, phones=None, emails=None, addresses=None, notes=""):
        self.id = id
        self.name = name or "Unidentified contact"
        self.phones = phones or []
        self.emails = emails or []
        self.addresses = addresses or []
        self.notes = notes

    def __str__(self):
        return (f"Contact(ID: {self.id}, Name: {self.name}, Phones: {self.phones}, "
                f"Emails: {self.emails}, Addresses: {self.addresses}, Notes: {self.notes})")
