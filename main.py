import sys
from ai.analyzer import analyze_file

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <python_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    print("🚀 CodeBrew - AI Code Optimizer")
    print("==============================\n")
    print(f"Analyzing file: {file_path}")
    
    result = analyze_file(file_path)
    if result:
        print(result)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 