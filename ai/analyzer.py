import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.github_utils import GitHubCodeFetcher
import requests
from .bedrock_client import BedrockClient
from utils.text_utils import clean_json_string
from utils.emailer import Emailer

# Load environment variables
load_dotenv()

# Configuration
region = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "1000"))
temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.1"))
suggestions_dir = os.getenv("SUGGESTIONS_DIR", "data/suggestions")
notification_email = os.getenv("NOTIFICATION_EMAIL")

# Initialize Bedrock client with explicit credentials
client = boto3.client(
    "bedrock-runtime",
    region_name=region,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

class CodeAnalyzer:
    def __init__(self):
        self.bedrock = BedrockClient()
        
    def analyze_code(self, code: str) -> Optional[Dict]:
        """Analyze code using AWS Bedrock"""
        prompt = f"""Analyze this code and suggest optimizations. Focus on:
1. Performance improvements
2. Code quality
3. Best practices
4. Potential bugs

Code to analyze:
{code}

Provide the analysis in this JSON format:
{{
    "issue": "Description of the issue found",
    "benefit": {{
        "explanation": "How this optimization helps",
        "impact": "High/Medium/Low"
    }},
    "suggestion": "Specific code suggestion"
}}"""

        try:
            response = self.bedrock.generate_text(prompt)
            return response
        except Exception as e:
            print(f"Error analyzing code: {str(e)}")
            return None

    def analyze_multiple_files(self, files: List[Dict]) -> Optional[Dict]:
        """Analyze multiple files and return the single highest-impact suggestion"""
        # Prepare the files section of the prompt
        files_section = "\n\n".join([
            f"File: {file['name']}\nPath: {file['path']}\n\n{file['content']}"
            for file in files
        ])

        # Read the prompt template
        try:
            with open('prompts/code_analysis.txt', 'r') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            print("Error: prompts/code_analysis.txt not found")
            return None
        except Exception as e:
            print(f"Error reading prompt template: {str(e)}")
            return None

        # Format the prompt with the files section
        prompt = prompt_template.format(files_section=files_section)

        try:
            response = self.bedrock.generate_text(prompt)
            if response:
                try:
                    # If response is already a dict, use it directly
                    if isinstance(response, dict):
                        return response
                        
                    # Otherwise, try to parse it as JSON string
                    cleaned_response = clean_json_string(response)
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    print(f"Error parsing analysis JSON: {str(e)}")
                    print("Raw response:", response)
                    return None
            return None
        except Exception as e:
            print(f"Error analyzing files: {str(e)}")
            return None

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
    """Save the AI suggestion to a JSON file and send email notification"""
    # Create data directory if it doesn't exist
    os.makedirs(suggestions_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{suggestions_dir}/suggestion_{timestamp}.json"
    
    # Save to file
    with open(filename, "w") as f:
        f.write(suggestion)

    print(f"\n💾 Suggestion saved to: {filename}")

    # Send email notification if email is configured
    if notification_email:
        try:
            print(f"\n📧 Sending email to: {notification_email}")
            emailer = Emailer()
            suggestion_data = json.loads(suggestion)
            
            # Format code blocks with proper indentation
            def format_code(code: str) -> str:
                if not code:
                    return "N/A"
                return code  # Preserve all indentation and formatting
            
            repo_name = 'rahulsinghal11/codebrew'  # Hardcoded correct repo name
            # Build the Create PR button URL
            pr_url = (
                f"http://localhost:8000/create_pr?"
                f"repo_name={repo_name}"
                f"&title={suggestion_data.get('commit_message', '')}"
                f"&body={suggestion_data.get('benefit', '')}"
                f"&head_branch={suggestion_data.get('branch_name', '')}"
                f"&base_branch=master"
            )

            # Create beautiful email body
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #2c3e50;
                        color: white;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .code-block {{
                        background-color: #f1f1f1;
                        padding: 15px;
                        border-radius: 5px;
                        font-family: 'Courier New', monospace;
                        white-space: pre;
                        margin: 10px 0;
                        overflow-x: auto;
                        tab-size: 4;
                    }}
                    .benefit {{
                        background-color: #e8f5e9;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        color: #666;
                        font-size: 0.9em;
                    }}
                    .pr-btn {{
                        display: inline-block;
                        padding: 12px 28px;
                        font-size: 1.1em;
                        color: #fff !important;
                        background-color: #1976d2;
                        border: none;
                        border-radius: 5px;
                        text-decoration: none;
                        margin: 20px 0;
                        font-weight: bold;
                        transition: background 0.2s;
                    }}
                    .pr-btn:hover {{
                        background-color: #125ea2;
                    }}
                    h1, h2, h3 {{
                        color: #2c3e50;
                    }}
                    .badge {{
                        display: inline-block;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: 0.8em;
                        margin-right: 10px;
                        background-color: #e3f2fd;
                        color: #1976d2;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    <h2>📝 Improvement Details</h2>
                    <p><strong>Repository:</strong> {repo_name}</p>
                    <p><strong>File:</strong> {file_analyzed}</p>
                    <p><strong>Issue:</strong> {suggestion_data.get('issue', 'N/A')}</p>
                    
                    <div class="benefit">
                        <h3>🎯 Benefit</h3>
                        <p>{suggestion_data.get('benefit', 'N/A')}</p>
                    </div>
                    
                    <h3>🔧 Code Changes</h3>
                    <p><strong>Original Code:</strong></p>
                    <div class="code-block">
{format_code(suggestion_data.get('old_code', 'N/A'))}
                    </div>
                    <p><strong>Improved Code:</strong></p>
                    <div class="code-block">
{format_code(suggestion_data.get('new_code', 'N/A'))}
                    </div>
                    <a href='{pr_url}' class='pr-btn' target='_blank'>🚀 Create PR</a>
                    <p>
                        <span class="badge">Commit</span> {suggestion_data.get('commit_message', 'N/A')}
                        <span class="badge">Branch</span> {suggestion_data.get('branch_name', 'N/A')}
                    </p>
                </div>
                
                <div class="footer">
                    <p>Generated by CodeBrew AI Code Optimizer</p>
                    <p>Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </body>
            </html>
            """
            
            result = emailer.send_email(
                to_email=notification_email,
                subject=f"✨ CodeBrew [{repo_name}]: {suggestion_data.get('commit_message', 'Code Improvement')}",
                body=body,
                is_html=True
            )
            
            if result["status"] == "success":
                print("📧 Email notification sent successfully")
            else:
                print(f"⚠️ Failed to send email notification: {result['message']}")
                
        except Exception as e:
            print(f"⚠️ Error sending email notification: {str(e)}")
    
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

def analyze_repository_structure(repo_info: Dict) -> List[Dict]:
    """Analyze repository structure to determine which files to analyze"""
    prompt = f"""You are an expert code reviewer. Analyze this repository structure and determine the top {repo_info['n_files']} most important files to review for optimization opportunities.

Repository: {repo_info['repository']['name']}
Owner: {repo_info['repository']['owner']}

Files in repository:
{json.dumps(repo_info['structure'], indent=2)}

IMPORTANT: Do NOT select any test files (files in test directories or files with 'test' in their name).

Consider these factors when selecting files:
1. Core functionality files
2. Files with complex logic
3. Files that might have performance bottlenecks
4. Files that are frequently modified
5. Files that are critical to the application
6. Files that are part of the main application code (not tests)

Return your response in this JSON format:
{{
    "selected_files": [
        {{
            "name": "path/to/file.py",
            "url": "file_url",
            "reason": "Why this file is important to analyze"
        }}
    ]
}}"""

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
            return json_suggestion["selected_files"]
        except json.JSONDecodeError as e:
            print(f"Error parsing repository analysis JSON: {str(e)}")
            print("Raw suggestion:", suggestion)
            return []
            
    except Exception as e:
        print(f"Error analyzing repository structure: {str(e)}")
        return []

def analyze_github_file(file_url: str) -> Optional[Dict]:
    """Analyze a file from GitHub"""
    try:
        # Get GitHub token from environment
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("Error: GITHUB_TOKEN not found in environment variables")
            return None
            
        # Get file content from GitHub
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3.raw"
        }
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        
        # Analyze the code
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_code(response.text)
        
        if analysis:
            # Save the suggestion
            save_suggestion(file_url, json.dumps(analysis, indent=2))
            
        return analysis
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file from GitHub: {str(e)}")
        return None
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return None

def analyze_github_files(file_urls: List[Dict]) -> Optional[Dict]:
    """Analyze multiple files from GitHub and return the highest-impact suggestion"""
    try:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GitHub token not found in environment variables")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Fetch file contents
        files_to_analyze = []
        for file_info in file_urls:
            try:
                response = requests.get(file_info['url'], headers=headers)
                response.raise_for_status()
                files_to_analyze.append({
                    'name': file_info['name'],
                    'path': file_info['name'],
                    'content': response.text
                })
            except Exception as e:
                print(f"Error fetching {file_info['name']}: {str(e)}")
        
        if not files_to_analyze:
            print("No files were successfully fetched")
            return None
        
        print(f"\n🔍 Successfully fetched {len(files_to_analyze)} files")
        
        # Analyze files using Bedrock
        bedrock_client = BedrockClient()
        analysis_result = bedrock_client.analyze_multiple_files(files_to_analyze)
        
        if analysis_result:
            # Save the analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suggestion_file = f"data/suggestions/suggestion_{timestamp}.json"
            
            # Print the analysis
            print(f"\n📝 Analysis for {analysis_result.get('file_name', analysis_result.get('file', 'unknown'))}:")
            print(f"Issue: {analysis_result.get('issue', 'No issue found')}")
            print(f"Benefit: {analysis_result.get('benefit', 'No benefit specified')}")
            if 'old_code' in analysis_result:
                print(f"\nOld code:")
                print(analysis_result['old_code'])
                print(f"\nNew code:")
                print(analysis_result['new_code'])
            
            # Save the full analysis
            save_suggestion(suggestion_file, json.dumps(analysis_result, indent=2))
            print(f"\n💾 Suggestion saved to: {suggestion_file}")
            
            return analysis_result
        
        return None
    except Exception as e:
        import traceback
        print("Error in analyze_github_files:")
        print(traceback.format_exc())
        return None

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