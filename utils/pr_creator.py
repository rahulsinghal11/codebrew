import requests, base64
import os
import json
from dotenv import load_dotenv


class PRCreator:
    def __init__(self, owner, repo, base_branch):
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.owner = owner
        self.repo = repo
        self.base_branch = base_branch

    def process_suggestion(self, suggestion_file: str) -> dict:
        """
        Process a suggestion file and create a PR with the changes
        
        Args:
            suggestion_file (str): Path to the suggestion JSON file
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Load suggestion data
            commit_msg, new_code, start_line, end_line, file_path, new_branch = self.load_suggestion(suggestion_file)
            
            # Create new branch from base
            self.create_branch(new_branch=new_branch)
            
            # Read file contents and update with new code
            updated_content, file_sha = self.get_file(
                file_path, new_code, start_line, end_line
            )
            
            # Commit and push to new branch
            self.update_file(file_path, updated_content,
                commit_msg, new_branch, file_sha)
            
            # Create pull request
            pr_result = self.create_pull_request(
                new_branch,
                commit_msg,
                "",  # Empty body for now
            )
            
            return {
                "success": True,
                "branch": new_branch,
                "pr": pr_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_branch_sha(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/ref/heads/{self.base_branch}"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "application/vnd.github+json"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        print(res.json())
        return res.json()["object"]["sha"]


    def create_branch(self, new_branch="ft/codebrew"):
        # Get SHA of base branch
        base_sha = self.get_branch_sha()

        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "application/vnd.github+json"}
        data = {
            "ref": f"refs/heads/{new_branch}",
            "sha": base_sha
        }
        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()


    def get_file(self, path, new_code, start_line, end_line):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}?ref={self.base_branch}"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "application/vnd.github+json"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        content = base64.b64decode(res.json()["content"]).decode("utf-8")

        # Split content into lines and replace specified range
        lines = content.splitlines()
        new_code_lines = new_code.splitlines()

        updated_lines = (
            lines[:start_line - 1] +    # lines before start_line (1-indexed)
            new_code_lines +           # replacement lines
            lines[end_line:]           # lines after end_line
        )

        updated_content = "\n".join(updated_lines) + "\n"  # Ensure final newline

        sha = res.json()["sha"]
        return updated_content, sha


    def update_file(self, path, new_content, commit_msg, branch, sha):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "application/vnd.github+json"}
        content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

        data = {
            "message": commit_msg,
            "content": content_encoded,
            "branch": branch,
            "sha": sha
        }

        res = requests.put(url, json=data, headers=headers)
        res.raise_for_status()


    def create_pull_request(self, head_branch, title, body):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "application/vnd.github+json"}
        data = {
            "title": title,
            "body": body,
            "head": f'{self.owner}:{head_branch}',  # The branch with your changes
            "base": self.base_branch   # The branch you want to merge into (e.g., main)
        }

        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()
        pr_url = res.json()["html_url"]
        print(f"Pull Request created: {pr_url}")
        return pr_url


    def load_suggestion(self, file_path):
        """Load a suggestion from a JSON file."""
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['commit_message'], data['new_code'], data['start_line'], data['end_line'], data['file_path'], data['branch_name']



if __name__ == "__main__":
    # Example usage
    creator = PRCreator()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    suggestions_path = os.path.join(script_dir, 'suggestions')
    
    # Process all suggestion files
    json_files = [os.path.join(suggestions_path, f) for f in os.listdir(suggestions_path) if f.endswith('.json')]
    for file_path in json_files:
        result = creator.process_suggestion(str(file_path))
        if result["success"]:
            print(f"Successfully processed {file_path}")
            # print(f"PR URL: {result['pr'].get('url', 'N/A')}")
        else:
            print(f"Error processing {file_path}: {result['error']}")


