def process_matrix(matrix):
    """Process a matrix and return its transpose"""
    rows = len(matrix)
    cols = len(matrix[0])
    
    # Create new matrix
    result = []
    for i in range(cols):
        row = []
        for j in range(rows):
            row.append(matrix[j][i])
        result.append(row)
    
    return result

# Example usage
if __name__ == "__main__":
    matrix = [[0] * 1000 for _ in range(1000)]
    matrix = [[i + j for j in range(1000)] for i in range(1000)]
    result = process_matrix(matrix)
    print(f"Matrix processed: {len(result)}x{len(result[0])}") 
