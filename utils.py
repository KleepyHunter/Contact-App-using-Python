# Exceptions
class ReturnToMainMenu(Exception):
    pass

class ReturnToPreviousStep(Exception):
    pass

def special_input(prompt, step=None):
    """
    Handles user input with options to return to the previous step or main menu.
    Adds current step to navigation history.
    """

    while True:
        user_input = input(prompt)
        if user_input.lower() == "cancel":
            print("Returning to the main menu...")
            raise ReturnToMainMenu
        elif user_input.lower() == "back":
            print("Returning to the previous step...")
            raise ReturnToPreviousStep
        return user_input