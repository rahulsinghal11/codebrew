def get_duplicates(arr):
    duplicates = []
    seen = set()
    for num in arr:
        if num in seen:
            duplicates.append(num)
        else:
            seen.add(num)
    return duplicates

# Example usage
if __name__ == "__main__":
    test_array = [1, 2, 3, 2, 4, 5, 3, 6]
    result = get_duplicates(test_array)
    print(f"Duplicates found: {result}") 