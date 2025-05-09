import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
region = os.getenv("AWS_REGION", "us-east-1")
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

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
- ✅ Performance (e.g., faster loops, better data structures)
- ✅ Readability or simplicity
- ✅ Removal of dead or unused code
- ✅ Using a cleaner or more Pythonic alternative
- ✅ Using internal tools or libraries if relevant

Only suggest changes that are **safe, local**, and **do not change the behavior** of the code.

🎯 **Your goal is to generate one actionable suggestion worth creating a pull request for.**

Return your response **strictly in this JSON format** (and nothing else):

{{
  "issue": "What is the problem or opportunity for improvement?",
  "old_code": "The original snippet (minimum necessary to understand the fix)",
  "new_code": "The improved version (clean, correct, tested)",
  "benefit": "A short explanation of why this change is useful. Include % improvement if it's a speed boost.",
  "commit_message": "A short GitHub-style commit message (no more than 10 words)"
}}

Example:

{{
  "issue": "Inefficient nested loops to find duplicates",
  "old_code": "for i in range(len(arr)):\\n    for j in range(i+1, len(arr)):\\n        if arr[i] == arr[j]:",
  "new_code": "seen = set()\\nfor item in arr:\\n    if item in seen:\\n        ...",
  "benefit": "Reduces time complexity from O(n^2) to O(n); ~80% faster on large inputs.",
  "commit_message": "Optimize duplicate search with set lookup"
}}

Here is the Python code to analyze:

{code}"""

    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
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
    os.makedirs("data/suggestions", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/suggestions/suggestion_{timestamp}.json"
    
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
        
        suggestion = analyze_python_code(code)
        if suggestion:
            save_suggestion(file_path, suggestion)
        return suggestion
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
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