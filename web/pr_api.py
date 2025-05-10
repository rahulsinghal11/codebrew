from fastapi import FastAPI, HTTPException
from utils.pr_creator import PRCreator
import json
from datetime import datetime
from pathlib import Path
import os

app = FastAPI()


def append_pr_to_data(suggestion, pr_info):
    data_path = Path("web/data/data.json")
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []
    # Calculate line counts
    old_code = suggestion.get('old_code', '')
    new_code = suggestion.get('new_code', '')
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()
    no_of_lines_optmized = min(len(old_lines), len(new_lines))
    no_of_unused_lines_removed = max(0, len(old_lines) - len(new_lines))
    # Build entry
    entry = {
        "file_path": suggestion.get('file_path', ''),
        "date": datetime.utcnow().strftime('%Y-%m-%d'),
        "repo_name": suggestion.get('repo_name', 'CodeBrew'),
        "optimization_summary": [
            suggestion.get('commit_message', ''),
            suggestion.get('benefit', '')
        ],
        "no_of_lines_optmized": no_of_lines_optmized,
        "no_of_unused_lines_removed": no_of_unused_lines_removed,
        "user": "Rahul"
    }
    data.append(entry)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.get("/create_pr")
async def create_pr(repo_name: str, owner: str, base_branch: str):
    """
    Create a pull request with the suggested changes
    
    Args:
        repo_name (str): Repository name (format: "owner/repo")
        title (str): PR title
        body (str): PR description
        head_branch (str): Branch containing changes
        base_branch (str): Target branch for PR
    """
    try:
        pr_creator = PRCreator(owner=owner, repo=repo_name, base_branch=base_branch)            # initialize the PR creator with api query params

        # Find the suggestion file for this branch
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        suggestions_path = os.path.join(script_dir, 'utils', 'suggestions')
        
        # Look for a JSON file that contains this branch name
        suggestion_file = None
        data = None
        for file in os.listdir(suggestions_path):
            if file.endswith('.json'):
                file_path = os.path.join(suggestions_path, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('repo_name') == repo_name:
                        suggestion_file = file_path
                        break
        
        try:
            result = pr_creator.process_suggestion(suggestion_file)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=result["error"])
            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn web.pr_api:app --reload 