def print_menu():

    print("\n=== Calculator ===")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Show History")
    print("6. Clear History")
    print("7. Safe Divide")
    print("8. Safe Power")
    print("9. Factorial")
    print("10. Percentage")
    print("11. Exit")


def get_number(message):

    while True:

        try:
            return float(input(message))

        except ValueError:
            print("Please enter a valid number")


def validate_choice(choice):

    valid_choices = {
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11"
    }

    return choice in valid_choices