def get_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# Example usage
if __name__ == "__main__":
    test_items = [1, 2, 3, 2, 4, 5, 3, 6]
    result = get_duplicates(test_items)
    print(f"Duplicates found: {result}") 