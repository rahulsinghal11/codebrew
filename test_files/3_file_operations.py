def process_large_file(filename):
    """Process a large file line by line"""
    result = []
    with open(filename, 'r') as file:
        for line in file:
            if line.strip():
            if line.strip():
                result.append(line.strip())
    return result

# Example usage
if __name__ == "__main__":
    # Create a test file
    with open('test.txt', 'w') as f:
        for i in range(1000):
            f.write(f"Line {i}\n")
    
    result = process_large_file('test.txt')
    print(f"Processed {len(result)} lines") 
