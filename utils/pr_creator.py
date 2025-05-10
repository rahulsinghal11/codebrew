import requests, base64
import os
from pathlib import Path
import json
from dotenv import load_dotenv
from github import Github

def get_branch_sha(owner, repo, branch, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    print(res.json())
    return res.json()["object"]["sha"]


def create_branch(owner, repo, sha, token, new_branch="ft/codebrew"):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    data = {
        "ref": f"refs/heads/{new_branch}",
        "sha": sha
    }
    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()


def get_file(owner, repo, path, branch, token, new_code, start_line, end_line):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
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


def update_file(owner, repo, path, new_content, commit_msg, branch, sha, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    data = {
        "message": commit_msg,
        "content": content_encoded,
        "branch": branch,
        "sha": sha
    }

    res = requests.put(url, json=data, headers=headers)
    res.raise_for_status()


def create_pull_request(owner, repo, head_branch, base_branch, title, body, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    data = {
        "title": title,
        "body": body,
        "head": f'{owner}:{head_branch}',  # The branch with your changes
        "base": base_branch   # The branch you want to merge into (e.g., main)
    }

    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()
    pr_url = res.json()["html_url"]
    print(f"Pull Request created: {pr_url}")
    return pr_url


def load_suggestion(file_path):
    """Load a suggestion from a JSON file."""
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['commit_message'], data['new_code'], data['start_line'], data['end_line'], data['file_path'], data['branch_name']

class PRCreator:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None
        self.owner = "rahulsinghal11"
        self.repo = "codebrew"
        self.base_branch = "master"
    
    def create_pull_request(self, repo_name: str, title: str, body: str, 
                          head_branch: str, base_branch: str = "master") -> dict:
        """
        Create a pull request on GitHub
        
        Args:
            repo_name (str): Repository name (format: "owner/repo")
            title (str): PR title
            body (str): PR description
            head_branch (str): Branch containing changes
            base_branch (str): Target branch for PR
            
        Returns:
            dict: Pull request details
        """
        try:
            if not self.github:
                raise ValueError("GitHub token not configured")
                
            repo = self.github.get_repo(repo_name)
            # Check if head_branch exists
            branches = [b.name for b in repo.get_branches()]
            if head_branch not in branches:
                # Create the branch from master
                base_branch_ref = repo.get_branch(base_branch)
                repo.create_git_ref(ref=f"refs/heads/{head_branch}", sha=base_branch_ref.commit.sha)
            try:
                pr = repo.create_pull(
                    title=title,
                    body=body,
                    head=head_branch,
                    base=base_branch
                )
                return {
                    "url": pr.html_url,
                    "number": pr.number,
                    "state": pr.state
                }
            except Exception as e:
                # If PR already exists, find and return it
                if hasattr(e, 'data') and e.data:
                    msg = str(e.data)
                else:
                    msg = str(e)
                if 'A pull request already exists' in msg:
                    # Find the existing PR for this branch
                    pulls = repo.get_pulls(state='open', head=f"{repo.owner.login}:{head_branch}")
                    for pr in pulls:
                        if pr.head.ref == head_branch:
                            return {
                                "url": pr.html_url,
                                "number": pr.number,
                                "state": pr.state,
                                "already_exists": True
                            }
                return {"error": msg}
        except Exception as e:
            return {"error": str(e)}

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
            commit_msg, new_code, start_line, end_line, file_path, new_branch = load_suggestion(suggestion_file)
            
            # Get SHA of base branch
            base_sha = get_branch_sha(self.owner, self.repo, self.base_branch, self.github_token)
            
            # Create new branch from base
            create_branch(self.owner, self.repo, base_sha, self.github_token, new_branch=new_branch)
            
            # Read file contents and update with new code
            updated_content, file_sha = get_file(
                self.owner, self.repo, file_path, self.base_branch, 
                self.github_token, new_code, start_line, end_line
            )
            
            # Commit and push to new branch
            update_file(
                self.owner, self.repo, file_path, updated_content,
                commit_msg, new_branch, file_sha, self.github_token
            )
            
            # Create pull request
            pr_result = self.create_pull_request(
                f"{self.owner}/{self.repo}",
                commit_msg,
                "",  # Empty body for now
                new_branch,
                self.base_branch
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
            print(f"PR URL: {result['pr'].get('url', 'N/A')}")
        else:
            print(f"Error processing {file_path}: {result['error']}")


