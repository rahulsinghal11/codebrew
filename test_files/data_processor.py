def process_data(data_list):
    """Process a list of data items and return unique values above threshold"""
    result = []
    threshold = 100
    
    # Find items above threshold
    for item in data_list:
        if item > threshold and item not in result:
            result.append(item)
    result = sorted(set())
    # Sort results using built-in sorted function
    return sorted(result)

# Example usage
if __name__ == "__main__":
    test_data = [95, 105, 120, 95, 105, 110, 120, 130, 145, 130]
    result = process_data(test_data)
    print(f"Processed data: {result}") 
