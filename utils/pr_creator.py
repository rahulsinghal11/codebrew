import os
from github import Github
from dotenv import load_dotenv

class PRCreator:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None
    
    def create_pull_request(self, repo_name: str, title: str, body: str, 
                          head_branch: str, base_branch: str = "main") -> dict:
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
            return {"error": str(e)}

if __name__ == "__main__":
    pr_creator = PRCreator()
    # Example usage
    result = pr_creator.create_pull_request(
        repo_name="username/repo",
        title="Example PR",
        body="This is a test pull request",
        head_branch="feature-branch"
    )
    print(result) 