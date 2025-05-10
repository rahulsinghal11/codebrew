from utils.github_utils import GitHubCodeFetcher
import os
from dotenv import load_dotenv

def test_github_fetcher():
    # Load environment variables
    load_dotenv()
    
    # Verify environment variables are loaded
    print("\nChecking environment variables...")
    print("GITHUB_TOKEN present:", "GITHUB_TOKEN" in os.environ)
    
    fetcher = GitHubCodeFetcher()
    
    # Test getting Python files from a public repository
    print("\nTesting get_python_files...")
    files = fetcher.get_python_files("https://github.com/pallets/flask")
    if files:
        print(f"\nFound {len(files)} Python files")
        # Print first 3 files as example
        for file in files[:3]:
            print(f"\nFile: {file['name']}")
            print(f"Path: {file['path']}")
            print(f"URL: {file['url']}")
            print(f"Size: {file['size']} bytes")
    else:
        print("No files found or error occurred")
    
    # Test fetching a specific file
    print("\nTesting fetch_code_from_github...")
    code = fetcher.fetch_code_from_github(
        "https://github.com/pallets/flask/blob/main/src/flask/__init__.py"
    )
    if code:
        print("\nSuccessfully fetched code:")
        print(code[:200] + "...") # Print first 200 characters
    else:
        print("Failed to fetch code")

if __name__ == "__main__":
    test_github_fetcher() 