import os
import random
import requests
from typing import Dict, List, Optional
from pathlib import Path

class RepoSelector:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")
            
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def get_default_branch(self, owner: str, repo: str) -> Optional[str]:
        """Get the default branch of a repository"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("default_branch", "main")
        except Exception as e:
            print(f"Error getting default branch: {str(e)}")
            return None
        
    def get_random_repo(self) -> Optional[Dict]:
        """Get a random repository from the list"""
        try:
            # Read repositories from file
            repo_file = Path("data/repositories.txt")
            if not repo_file.exists():
                print("Error: repositories.txt not found")
                return None
                
            with open(repo_file) as f:
                repos = [line.strip() for line in f if line.strip()]
                
            if not repos:
                print("Error: No repositories found in file")
                return None
                
            # Select random repository
            repo_url = random.choice(repos)
            repo_name = repo_url.split("/")[-1]
            owner = repo_url.split("/")[-2]
            
            return {
                "url": repo_url,
                "name": repo_name,
                "owner": owner,
                "default_branch": "main"  # Using main as default branch
            }
            
        except Exception as e:
            print(f"Error getting random repository: {str(e)}")
            return None
            
    def get_repo_structure(self, repo: Dict) -> List[Dict]:
        """Get repository structure with metadata"""
        def traverse_directory(path: str) -> List[Dict]:
            """Recursively traverse directory and get all Python files"""
            try:
                api_url = f"https://api.github.com/repos/{repo['owner']}/{repo['name']}/contents/{path}"
                response = requests.get(api_url, headers=self.headers)
                response.raise_for_status()
                
                items = response.json()
                if not isinstance(items, list):
                    return []
                    
                structure = []
                for item in items:
                    if item["type"] == "file" and item["name"].endswith(".py"):
                        structure.append({
                            "name": item["path"],
                            "url": item["download_url"],
                            "size": item["size"],
                            "type": "file",
                            "language": "Python"
                        })
                    elif item["type"] == "dir":
                        # Skip test directories
                        if "test" not in item["path"].lower():
                            # Recursively get files from subdirectory
                            structure.extend(traverse_directory(item["path"]))
                
                return structure
                
            except Exception as e:
                print(f"Error traversing directory {path}: {str(e)}")
                return []

        try:
            # Start traversal from root
            structure = traverse_directory("")
            
            if not structure:
                # If root is empty, try src directory
                structure = traverse_directory("src")
            
            print(f"\nFound Python files in directories:")
            # Print unique directories to help debug
            dirs = set()
            for file in structure:
                dir_path = os.path.dirname(file["name"])
                if dir_path:
                    dirs.add(dir_path)
            for dir_path in sorted(dirs):
                print(f"  - {dir_path}")
                
            return structure
            
        except Exception as e:
            print(f"Error getting repository structure: {str(e)}")
            return []
            
    def analyze_repository(self, n_files: int = 5) -> Optional[Dict]:
        """Analyze a random repository and return top N files"""
        # Get random repository
        repo = self.get_random_repo()
        if not repo:
            return None
            
        print(f"\n📦 Selected repository: {repo['name']} (branch: {repo['default_branch']})")
        
        # Get repository structure
        structure = self.get_repo_structure(repo)
        if not structure:
            print("No Python files found in repository")
            return None
            
        print(f"Found {len(structure)} Python files")
        
        # Return repository info and structure for Bedrock analysis
        return {
            "repository": repo,
            "structure": structure,
            "n_files": n_files
        }

if __name__ == "__main__":
    # Example usage
    selector = RepoSelector()
    result = selector.analyze_repository(n_files=3)
    
    if result:
        print("\n✅ Repository analysis complete!")
    else:
        print("\n❌ Repository analysis failed!") 