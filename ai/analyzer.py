import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from utils.github_utils import GitHubCodeFetcher

# Load environment variables
load_dotenv()

# Configuration
region = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "1000"))
temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.1"))
suggestions_dir = os.getenv("SUGGESTIONS_DIR", "data/suggestions")

# Initialize Bedrock client
client = boto3.client("bedrock-runtime", region_name=region)

def clean_json_string(text: str) -> str:
    """Clean JSON string by removing markdown code block markers"""
    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
    if text.endswith("```"):
        text = text.replace("```", "", 1)
    return text.strip()

def analyze_python_code(code: str) -> str:
    """Analyze Python code and return improvement suggestions"""
    prompt = f"""You are an expert AI code reviewer helping developers clean and improve codebases.

You will receive a single Python file. Analyze it carefully and identify **ONE specific, high-impact suggestion** that improves the code in one of these ways:
- ✅ Performance (e.g., faster loops, better data structures, optimized SQL queries)
- ✅ Readability or simplicity
- ✅ Removal of dead or unused code
- ✅ Using a cleaner or more Pythonic alternative
- ✅ Using internal tools or libraries if relevant
- ✅ SQL query optimization (e.g., adding indexes, rewriting queries, using better joins)
- ✅ Import optimization (moving heavy/single-use imports into specific functions)

Only suggest changes that are **safe, local**, and **do not change the behavior** of the code.

🎯 **Your goal is to generate one actionable suggestion worth creating a pull request for.**

IMPORTANT: When providing code snippets, you MUST:
1. Preserve ALL original indentation and formatting
2. Include the exact same number of spaces/tabs as the original code
3. Keep the same line breaks and alignment
4. Only change the specific lines that need improvement
5. Keep all surrounding context intact

Return your response **strictly in this JSON format** (and nothing else):

{{
  "issue": "What is the problem or opportunity for improvement?",
  "repo_name": "Name of the repository",
  "file_path": "Path relative to repository root",
  "file_name": "Name of the file being modified",
  "start_line": "Line number where the change starts (1-based)",
  "end_line": "Line number where the change ends (1-based)",
  "old_code": "The original snippet with exact indentation and formatting",
  "new_code": "The improved version with identical indentation and formatting",
  "benefit": "A short explanation of why this change is useful. Include % improvement if it's a speed boost.",
  "commit_message": "A short GitHub-style commit message (no more than 10 words)",
  "branch_name": "A descriptive branch name in kebab-case format (e.g., optimize-list-operations, fix-memory-leak)"
}}

Example with preserved formatting:

{{
  "issue": "Inefficient nested loops to find duplicates",
  "repo_name": "codebrew",
  "file_path": "src/utils/duplicate_finder.py",
  "file_name": "duplicate_finder.py",
  "start_line": 10,
  "end_line": 15,
  "old_code": "    for i in range(len(arr)):\\n        for j in range(i+1, len(arr)):\\n            if arr[i] == arr[j]:\\n                duplicates.append(arr[i])",
  "new_code": "    seen = set()\\n    for item in arr:\\n        if item in seen:\\n            duplicates.append(item)\\n        seen.add(item)",
  "benefit": "Reduces time complexity from O(n^2) to O(n); ~80% faster on large inputs.",
  "commit_message": "Optimize duplicate search with set lookup",
  "branch_name": "optimize-duplicate-search"
}}

Example with SQL (preserving formatting):

{{
  "issue": "Inefficient SQL query with multiple subqueries",
  "repo_name": "codebrew",
  "file_path": "src/db/queries.py",
  "file_name": "queries.py",
  "start_line": 25,
  "end_line": 30,
  "old_code": "    query = '''\\n        SELECT * FROM users\\n        WHERE id IN (\\n            SELECT user_id FROM orders\\n            WHERE total > 100\\n        )\\n        AND id IN (\\n            SELECT user_id FROM payments\\n            WHERE status = 'completed'\\n        )\\n    '''",
  "new_code": "    query = '''\\n        SELECT DISTINCT u.*\\n        FROM users u\\n        JOIN orders o ON u.id = o.user_id\\n        JOIN payments p ON u.id = p.user_id\\n        WHERE o.total > 100\\n        AND p.status = 'completed'\\n    '''",
  "benefit": "Reduces query execution time by ~60% by eliminating subqueries and using proper joins.",
  "commit_message": "Optimize user query with proper joins",
  "branch_name": "optimize-user-query-joins"
}}

Example with Import Optimization (preserving formatting):

{{
  "issue": "Heavy pandas import used only in one function",
  "repo_name": "codebrew",
  "file_path": "src/data/processor.py",
  "file_name": "processor.py",
  "start_line": 1,
  "end_line": 5,
  "old_code": "import pandas as pd\\nimport numpy as np\\n\\ndef process_data(data):\\n    df = pd.DataFrame(data)\\n    return df.mean()",
  "new_code": "def process_data(data):\\n    import pandas as pd\\n    df = pd.DataFrame(data)\\n    return df.mean()",
  "benefit": "Reduces module import time by ~200ms and memory usage by ~50MB when pandas is not needed.",
  "commit_message": "Move pandas import into function scope",
  "branch_name": "optimize-pandas-import"
}}

Here is the Python code to analyze:

{code}"""

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })
        )
        
        response_body = json.loads(response['body'].read())
        suggestion = response_body['content'][0]['text']
        
        try:
            # Clean and parse the JSON response
            cleaned_suggestion = clean_json_string(suggestion)
            json_suggestion = json.loads(cleaned_suggestion)

            # Format and print the suggestion in a readable way
            print("\n📝 AI Suggestion:")
            print(f"\n🔍 Issue:")
            print(json_suggestion["issue"])
            print(f"\n📄 Original Code:")
            print(json_suggestion["old_code"])
            print(f"\n✨ Improved Code:")
            print(json_suggestion["new_code"])
            print(f"\n📈 Benefit:")
            print(json_suggestion["benefit"])
            print(f"\n💬 Commit Message:")
            print(json_suggestion["commit_message"])
            print(f"\n🌿 Branch Name:")
            print(json_suggestion["branch_name"])
            
            return cleaned_suggestion
        except json.JSONDecodeError as e:
            print(f"Error parsing suggestion JSON: {str(e)}")
            print("Raw suggestion:", suggestion)
            return None
            
    except Exception as e:
        print(f"Error analyzing code: {str(e)}")
        return None

def save_suggestion(file_analyzed: str, suggestion: str) -> str:
    """Save the AI suggestion to a JSON file"""
    # Create data directory if it doesn't exist
    os.makedirs(suggestions_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{suggestions_dir}/suggestion_{timestamp}.json"
    
    # Save to file
    with open(filename, "w") as f:
        f.write(suggestion)

    print(f"\n💾 Suggestion saved to: {filename}")
    return filename

def analyze_file(file_path: str) -> str:
    """Analyze a Python file and return improvement suggestions"""
    try:
        print(f"\n📂 Reading file: {file_path}")
        with open(file_path, "r") as f:
            code = f.read()

        # Get file information
        file_name = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path)

        # Get repository name from git
        try:
            import subprocess
            repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip()
            repo_name = repo_url.split('/')[-1].replace('.git', '')
        except:
            repo_name = "codebrew"  # Default if git command fails

        # Add file information to the code
        code_with_info = f"""Repository: {repo_name}
File: {file_name}
Path: {rel_path}

{code}"""

        suggestion = analyze_python_code(code_with_info)
        if suggestion:
            save_suggestion(file_path, suggestion)
        return suggestion
    except Exception as e:
        print(f"⚠️ Error reading file {file_path}: {str(e)}")
        return {}

def analyze_github_file(github_url: str) -> Dict[str, Any]:
    """
    Analyze a Python file from GitHub and return improvement suggestions

    Args:
        github_url (str): GitHub URL to the Python file to analyze

    Returns:
        Dict[str, Any]: Analysis results with issue, code changes, benefit, and commit message
    """
    try:
        print(f"🔗 Fetching code from GitHub: {github_url}")
        fetcher = GitHubCodeFetcher()
        code = fetcher.fetch_code_from_github(github_url)

        if not code:
            print("⚠️ Failed to fetch code from GitHub")
            return {}

        return analyze_code_with_bedrock(code)

    except Exception as e:
        print(f"⚠️ Error analyzing GitHub file: {str(e)}")
        return {}

if __name__ == "__main__":
    # Example usage
    sample_code = """
    def get_duplicates(items):
        duplicates = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j]:
                    duplicates.append(items[i])
        return duplicates
    """
    
    # Create a temporary file for testing
    test_file = "sample.py"
    with open(test_file, "w") as f:
        f.write(sample_code)
    
    try:
        result = analyze_file(test_file)
        print(result)
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file) 