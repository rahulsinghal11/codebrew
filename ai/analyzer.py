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

    def analyze_multiple_files(self, files: List[Dict]) -> List[Dict]:
        """Analyze multiple files in a single Bedrock request"""
        # Prepare the files section of the prompt
        files_section = "\n\n".join([
            f"File: {file['name']}\nPath: {file['path']}\n\n{file['content']}"
            for file in files
        ])

        prompt = f"""You are an expert code reviewer. Analyze these files and suggest optimizations for each one. Focus on:
1. Performance improvements
2. Code quality
3. Best practices
4. Potential bugs

Files to analyze:

{files_section}

Provide the analysis in this JSON format:
{{
    "analyses": [
        {{
            "file": "filename.py",
            "issue": "Description of the issue found",
            "benefit": {{
                "explanation": "How this optimization helps",
                "impact": "High/Medium/Low"
            }},
            "suggestion": "Specific code suggestion"
        }},
        // ... one entry per file
    ]
}}"""

        try:
            response = self.bedrock.generate_text(prompt)
            if response:
                try:
                    # If response is already a dict, use it directly
                    if isinstance(response, dict):
                        return response.get("analyses", [])
                        
                    # Otherwise, try to parse it as JSON string
                    cleaned_response = clean_json_string(response)
                    json_response = json.loads(cleaned_response)
                    return json_response.get("analyses", [])
                except json.JSONDecodeError as e:
                    print(f"Error parsing analysis JSON: {str(e)}")
                    print("Raw response:", response)
                    return []
            return []
        except Exception as e:
            print(f"Error analyzing files: {str(e)}")
            return []

def clean_json_string(text: str) -> str:
    """Clean JSON string by removing markdown code block markers"""
    if isinstance(text, dict):
        return text
    if isinstance(text, str):
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text.replace("```", "", 1)
        return text.strip()
    return text

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

def analyze_github_files(file_urls: List[Dict]) -> List[Dict]:
    """Analyze multiple files from GitHub"""
    try:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GitHub token not found in environment variables")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3.raw'
        }
        
        # Fetch file contents and build dependency graph
        files_to_analyze = []
        dependency_graph = {}
        
        for file_info in file_urls:
            try:
                response = requests.get(file_info['url'], headers=headers)
                response.raise_for_status()
                content = response.text
                
                # Simple import analysis to build dependency graph
                imports = []
                for line in content.split('\n'):
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line.strip())
                
                file_name = file_info['name']
                dependency_graph[file_name] = imports
                
                files_to_analyze.append({
                    'name': file_name,
                    'path': file_info['url'],
                    'content': content,
                    'dependencies': imports,
                    'type': 'core' if 'app.py' in file_name or 'core' in file_name else 'module'
                })
                
            except requests.exceptions.RequestException as e:
                import traceback
                print(f"Error fetching file {file_info['name']}:")
                print(traceback.format_exc())
                continue
        
        if not files_to_analyze:
            print("No files were successfully fetched")
            return []
        
        # Prepare structured data for analysis
        structured_data = {
            'repository': {
                'name': 'flask',
                'branch': 'main',
                'total_files': len(files_to_analyze)
            },
            'files': files_to_analyze,
            'analysis_requirements': {
                'focus_areas': [
                    'Code quality and maintainability',
                    'Performance optimization',
                    'Security considerations',
                    'Best practices'
                ],
                'priority_files': [f['name'] for f in files_to_analyze if f['type'] == 'core']
            }
        }
        
        # Analyze files using Bedrock
        bedrock_client = BedrockClient()
        analysis_results = bedrock_client.analyze_structured_data(structured_data)
        
        if analysis_results:
            # Save all analyses in a single JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suggestion_file = f"data/suggestions/suggestion_{timestamp}.json"
            
            # Print each analysis
            if isinstance(analysis_results, dict) and 'analyses' in analysis_results:
                for analysis in analysis_results['analyses']:
                    print(f"\n📝 Analysis for {analysis['file']}:")
                    print(f"Issue: {analysis['issue']}")
                    print(f"Benefit: {analysis['benefit']['explanation']}")
            
            # Save the full analysis
            save_suggestion(suggestion_file, json.dumps(analysis_results, indent=2))
            print(f"\n💾 Suggestion saved to: {suggestion_file}")
            
            return analysis_results['analyses'] if 'analyses' in analysis_results else []
        
        return []
    except Exception as e:
        import traceback
        print("Error in analyze_github_files:")
        print(traceback.format_exc())
        return []

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