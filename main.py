import sys
import os
from pathlib import Path
from ai.analyzer import analyze_file

def analyze_directory(directory_path: str):
    """Analyze all Python files in a directory"""
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist")
        return
        
    python_files = list(directory.glob("**/*.py"))
    if not python_files:
        print(f"No Python files found in '{directory_path}'")
        return
        
    print(f"\nFound {len(python_files)} Python files to analyze")
    for file_path in python_files:
        print(f"\n📄 Analyzing: {file_path}")
        result = analyze_file(str(file_path))
        if result:
            print(result)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <python_file_or_directory>")
        sys.exit(1)
        
    path = sys.argv[1]
    print("🚀 CodeBrew - AI Code Optimizer")
    print("==============================\n")
    
    if os.path.isdir(path):
        print(f"Analyzing directory: {path}")
        analyze_directory(path)
    else:
        print(f"Analyzing file: {path}")
        result = analyze_file(path)
        if result:
            print(result)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 