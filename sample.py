def get_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                duplicates.append(arr[i])
    return duplicates

# Example usage
if __name__ == "__main__":
    test_array = [1, 2, 3, 2, 4, 5, 3, 6]
    result = get_duplicates(test_array)
    print(f"Duplicates found: {result}") 