def read_multiple_files(file_paths):
    """Read multiple files and combine their contents"""
    all_contents = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                all_contents.append(content)
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
    return all_contents

def write_combined_file(output_path, contents):
    """Write combined contents to a file"""
    try:
        with open(output_path, 'w') as file:
            for content in contents:
                file.write(content + '\n')
    except Exception as e:
        print(f"Error writing to {output_path}: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Create some test files
    test_files = ['test1.txt', 'test2.txt', 'test3.txt']
    for i, file_name in enumerate(test_files):
        with open(file_name, 'w') as f:
            f.write(f"Content of test file {i+1}")
    
    # Read and combine files
    contents = read_multiple_files(test_files)
    write_combined_file('combined.txt', contents)
    
    # Clean up test files
    for file_name in test_files:
        try:
            import os
            os.remove(file_name)
        except Exception as e:
            print(f"Error removing {file_name}: {str(e)}") 