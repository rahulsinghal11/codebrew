from pathlib import Path

def read_multiple_files(file_paths):
    """Read multiple files and combine their contents"""
    all_contents = []
    for file_path in file_paths:
        try:
            content = Path(file_path).read_text()
            all_contents.append(content)
        except OSError:
            print(f"Error reading {file_path}")
    return all_contents

def write_combined_file(output_path, contents):
    """Write combined contents to a file"""
    try:
        Path(output_path).write_text('\n'.join(contents))
    except OSError:
        print(f"Error writing to {output_path}")

# Example usage
if __name__ == "__main__":
    # Create some test files
    test_files = [Path('test1.txt'), Path('test2.txt'), Path('test3.txt')]
    for i, file_path in enumerate(test_files, start=1):
        file_path.write_text(f"Content of test file {i}")
    
    # Read and combine files
    contents = read_multiple_files(map(str, test_files))
    write_combined_file('combined.txt', contents)
    
    # Clean up test files
    for file_path in test_files:
        try:
            file_path.unlink()
        except OSError:
            print(f"Error removing {file_path}")
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
