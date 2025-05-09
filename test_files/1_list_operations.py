def find_common_elements(list1, list2):
    """Find common elements between two lists"""
    common = list(set(list1) & set(list2))
    return common

# Example usage
if __name__ == "__main__":
    list1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    list2 = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    result = find_common_elements(list1, list2)
    print(f"Common elements: {result}") 
