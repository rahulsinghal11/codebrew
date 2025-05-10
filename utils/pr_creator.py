import requests, base64
import os
from pathlib import Path
import json

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


if __name__ == "__main__":
    
    OWNER = "rahulsinghal11"
    REPO = "codebrew"
    BASE_BRANCH = "master"
    TOKEN = os.getenv('GITHUB_TOKEN')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    suggestions_path = os.path.join(script_dir, 'suggestions')
    json_files = [os.path.join(suggestions_path, f) for f in os.listdir(suggestions_path) if f.endswith('.json')]
    suggestions = []
    for file_path in json_files:
        try:
            COMMIT_MSG, NEW_CODE, START_LINE, END_LINE, FILE_PATH, NEW_BRANCH = load_suggestion(str(file_path))
            # print(f"Loaded suggestion from {file_path}")

            # 1. Get SHA of base branch
            base_sha = get_branch_sha(OWNER, REPO, BASE_BRANCH, TOKEN)

            # 2. Create new branch from base
            create_branch(OWNER, REPO, base_sha, TOKEN, new_branch=NEW_BRANCH)

            # 3. Read file contents from base branch
            updated_content, file_sha = get_file(OWNER, REPO, FILE_PATH, BASE_BRANCH, TOKEN, NEW_CODE, START_LINE, END_LINE)

            # 5. Commit and push to new branch
            update_file(OWNER, REPO, FILE_PATH, updated_content, COMMIT_MSG, NEW_BRANCH, file_sha, TOKEN)

            create_pull_request(OWNER, REPO, NEW_BRANCH, BASE_BRANCH, COMMIT_MSG, "", TOKEN)

            print(f"Changes pushed to branch {NEW_BRANCH}")

        except Exception as e:
            print(f"Error loading suggestion from {file_path}: {str(e)}")


