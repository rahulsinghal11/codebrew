def divide_numbers(a, b):
    """Divide two numbers"""
    try:
        result = a / b
    except ZeroDivisionError:
        print(f"Error: Cannot divide {a} by 0")
        return None

def process_division(numbers):
    """Process a list of number pairs"""
    results = []
    for i in range(0, len(numbers), 2):
        if i + 1 < len(numbers):
            result = divide_numbers(numbers[i], numbers[i + 1])
            if result is not None:
                results.append(result)
    return results

# Example usage
if __name__ == "__main__":
    numbers = [10, 2, 5, 0, 8, 4, 6, 2]
    results = process_division(numbers)
    print("Division results:", results) 
