def get_duplicates(arr):
    seen = set()
    duplicates = set()
    for num in arr:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    return list(duplicates)

# Example usage
if __name__ == "__main__":
    # Small test case
    test_array = [1, 2, 3, 2, 4, 5, 3, 6]
    result = get_duplicates(test_array)
    print(f"Small test - Duplicates found: {result}")
    
    # Large test case
    import random
    large_array = [random.randint(1, 1000) for _ in range(10000)]
    result = get_duplicates(large_array)
    print(f"Large test - Number of duplicates found: {len(result)}") 