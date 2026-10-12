def safe_divide(a, b):
    """
    Division that handles edge cases safely.
    Returns None instead of crashing on invalid input.
    """

    if b == 0:
        return None

    return a / b


def safe_power(a, b):
    """
    Safe exponentiation with basic overflow protection.
    """

    try:
        result = a ** b

        # basic sanity check for infinities
        if result == float("inf") or result == float("-inf"):
            return None

        return result

    except (OverflowError, ValueError):
        return None


def factorial(n):
    """
    Iterative factorial with validation.
    Returns None for invalid input.
    """

    if not isinstance(n, int):
        return None

    if n < 0:
        return None

    result = 1

    for i in range(2, n + 1):
        result *= i

    return result


def percentage(value, total):
    """
    Compute percentage safely.
    """

    if total == 0:
        return None

    return (value / total) * 100