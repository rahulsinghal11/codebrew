import os
from github import Github
from dotenv import load_dotenv
from typing import Optional, Tuple, List, Dict
from urllib.parse import urljoin

class GitHubCodeFetcher:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None

    def get_repo_and_file_path(self, github_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse GitHub URL to get repository name and file path
        
        Args:
            github_url (str): GitHub URL (e.g., https://github.com/owner/repo/blob/branch/path/to/file.py)
            
        Returns:
            Tuple[str, str]: (repository_name, file_path) or (None, None) if invalid URL
        """
        try:
            # Remove trailing slash if present
            github_url = github_url.rstrip('/')
            
            # Split URL into parts
            parts = github_url.split('github.com/')
            if len(parts) != 2:
                return None, None
                
            # Get the part after github.com/
            path_parts = parts[1].split('/')
            if len(path_parts) < 4:  # owner/repo/blob/branch/path
                return None, None
                
            # Extract repository name and file path
            owner = path_parts[0]
            repo = path_parts[1]
            file_path = '/'.join(path_parts[4:])  # Skip 'blob' and branch name
            
            return f"{owner}/{repo}", file_path
            
        except Exception as e:
            print(f"Error parsing GitHub URL: {str(e)}")
            return None, None

    def get_repo_from_url(self, github_url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse GitHub URL to get repository name and branch
        
        Args:
            github_url (str): GitHub URL (e.g., https://github.com/owner/repo)
            
        Returns:
            Tuple[str, str, str]: (repository_name, branch, base_url) or (None, None, None) if invalid URL
        """
        try:
            # Remove trailing slash if present
            github_url = github_url.rstrip('/')
            
            # Split URL into parts
            parts = github_url.split('github.com/')
            if len(parts) != 2:
                return None, None, None
                
            # Get the part after github.com/
            path_parts = parts[1].split('/')
            if len(path_parts) < 2:  # Need at least owner/repo
                return None, None, None
                
            # Extract repository name and branch
            owner = path_parts[0]
            repo = path_parts[1]
            branch = "main"  # Default branch
            
            # If branch is specified in URL, use it
            if len(path_parts) > 2 and path_parts[2] == "tree":
                branch = path_parts[3]
            
            base_url = f"https://github.com/{owner}/{repo}/blob/{branch}"
            return f"{owner}/{repo}", branch, base_url
            
        except Exception as e:
            print(f"Error parsing GitHub URL: {str(e)}")
            return None, None, None

    def fetch_code_from_github(self, github_url: str) -> Optional[str]:
        """
        Fetch code from a GitHub repository
        
        Args:
            github_url (str): GitHub URL to the file
            
        Returns:
            str: File contents or None if error
        """
        try:
            if not self.github:
                raise ValueError("GitHub token not configured")
            
            repo_name, file_path = self.get_repo_and_file_path(github_url)
            if not repo_name or not file_path:
                raise ValueError("Invalid GitHub URL format")
            
            repo = self.github.get_repo(repo_name)
            file_content = repo.get_contents(file_path)
            
            # GitHub API returns content in base64
            import base64
            decoded_content = base64.b64decode(file_content.content).decode('utf-8')
            return decoded_content
            
        except Exception as e:
            print(f"Error fetching code from GitHub: {str(e)}")
            return None

    def get_python_files(self, github_url: str) -> List[Dict[str, str]]:
        """
        Get all Python files from a GitHub repository
        
        Args:
            github_url (str): GitHub repository URL
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing file information:
                {
                    'name': 'filename.py',
                    'path': 'path/to/file.py',
                    'url': 'https://github.com/owner/repo/blob/branch/path/to/file.py',
                    'size': 1234  # file size in bytes
                }
        """
        try:
            if not self.github:
                raise ValueError("GitHub token not configured")
            
            repo_name, branch, base_url = self.get_repo_from_url(github_url)
            if not repo_name:
                raise ValueError("Invalid GitHub URL format")
            
            repo = self.github.get_repo(repo_name)
            python_files = []
            
            # Get all contents recursively
            contents = repo.get_contents("", ref=branch)
            
            def process_contents(contents):
                for content in contents:
                    if content.type == "dir":
                        # Recursively process subdirectories
                        process_contents(repo.get_contents(content.path, ref=branch))
                    elif content.type == "file" and content.name.endswith('.py'):
                        # Add Python file to the list
                        file_url = urljoin(base_url, content.path)
                        python_files.append({
                            'name': content.name,
                            'path': content.path,
                            'url': file_url,
                            'size': content.size
                        })
            
            process_contents(contents)
            return python_files
            
        except Exception as e:
            print(f"Error getting Python files: {str(e)}")
            return []

if __name__ == "__main__":
    # Example usage
    fetcher = GitHubCodeFetcher()
    
    # Example 1: Get a single file
    code = fetcher.fetch_code_from_github(
        "https://github.com/username/repo/blob/main/path/to/file.py"
    )
    if code:
        print("Successfully fetched code:")
        print(code)
    else:
        print("Failed to fetch code")
    
    # Example 2: Get all Python files
    python_files = fetcher.get_python_files("https://github.com/username/repo")
    if python_files:
        print("\nFound Python files:")
        for file in python_files:
            print(f"\nFile: {file['name']}")
            print(f"Path: {file['path']}")
            print(f"URL: {file['url']}")
            print(f"Size: {file['size']} bytes")
    else:
        print("No Python files found or error occurred") 