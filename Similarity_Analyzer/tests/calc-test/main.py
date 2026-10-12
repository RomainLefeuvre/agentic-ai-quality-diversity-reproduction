from op.operations import (
    add,
    subtract,
    multiply,
    divide
)

from utils import (
    get_number,
    print_menu,
    validate_choice
)

from op.history import (
    save_history,
    show_history,
    clear_history
)

from op.special_cases.calc_special import (
    safe_divide,
    safe_power,
    factorial,
    percentage
)


def run_calculator():

    while True:

        print_menu()
        choice = input("Choose an operation: ")

        result = None
        expression = None

        if not validate_choice(choice):
            print("Invalid option\n")
            continue

        # -------------------------
        # BASIC OPERATIONS (1–4)
        # -------------------------
        if choice in ["1", "2", "3", "4"]:

            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")

            if choice == "1":
                result = add(a, b)
                expression = f"{a} + {b} = {result}"

            elif choice == "2":
                result = subtract(a, b)
                expression = f"{a} - {b} = {result}"

            elif choice == "3":
                result = multiply(a, b)
                expression = f"{a} * {b} = {result}"

            elif choice == "4":
                result = divide(a, b)
                expression = f"{a} / {b} = {result}"

        # -------------------------
        # SAFE / SPECIAL OPS
        # -------------------------
        elif choice == "5":
            show_history()
            continue

        elif choice == "6":
            clear_history()
            continue

        elif choice == "7":
            a = get_number("Enter numerator: ")
            b = get_number("Enter denominator: ")
            result = safe_divide(a, b)
            expression = f"{a} / {b} (safe) = {result}"

        elif choice == "8":
            a = get_number("Enter base: ")
            b = get_number("Enter exponent: ")
            result = safe_power(a, b)
            expression = f"{a} ^ {b} = {result}"

        elif choice == "9":
            a = int(get_number("Enter n: "))
            result = factorial(a)
            expression = f"{a}! = {result}"

        elif choice == "10":
            a = get_number("Enter value: ")
            b = get_number("Enter total: ")
            result = percentage(a, b)
            expression = f"{a}/{b} * 100 = {result}"

        elif choice == "11":
            print("Goodbye!")
            break

        # -------------------------
        # OUTPUT + HISTORY
        # -------------------------
        if result is not None:
            print(f"Result: {result}")

        if expression is not None:
            save_history(expression)


def main():
    run_calculator()


if __name__ == "__main__":
    main()