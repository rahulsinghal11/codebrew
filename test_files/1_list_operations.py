def find_common_elements(list1, list2):
    """Find common elements between two lists"""
    common = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2 and item1 not in common:
                common.append(item1)
    return common

# Example usage
if __name__ == "__main__":
    list1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    list2 = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    result = find_common_elements(list1, list2)
    print(f"Common elements: {result}") 