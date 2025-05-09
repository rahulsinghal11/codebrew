import requests, base64

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
    print(f"✅ Pull Request created: {pr_url}")
    return pr_url



if __name__ == "__main__":
    
    OWNER = "rahulsinghal11"
    REPO = "codebrew"
    BASE_BRANCH = "master"
    NEW_BRANCH = "ft/codebrew2"
    FILE_PATH = "test_files/1_list_operations.py"
    TOKEN = os.getenv('GITHUB_TOKEN')
    COMMIT_MSG = "Optimize find_common_elements with set operations"
    NEW_CODE, START_LINE, END_LINE = "common = list(set(list1) & set(list2))", 3, 8

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

