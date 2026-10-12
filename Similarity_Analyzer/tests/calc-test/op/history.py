HISTORY = []


def save_history(entry):
    HISTORY.append(entry)


def show_history():

    if not HISTORY:
        print("No history available")
        return

    print("\n=== History ===")

    for item in HISTORY:
        print(item)


def clear_history():

    HISTORY.clear()

    print("History cleared")