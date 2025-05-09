import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configuration
region = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-7-sonnet-20250219-v1:0")

# Initialize Bedrock client
client = boto3.client("bedrock-runtime", region_name=region)

def build_prompt(code: str) -> str:
    """Build the prompt for Claude with the code to analyze"""
    return f"""
You are an AI code reviewer.

Review the following Python code and suggest one important improvement.
Respond in this JSON format:

{{
  "issue": "What needs to be improved",
  "old_code": "the original code block",
  "new_code": "the improved version",
  "benefit": "e.g. 30% speedup, cleaner, or removes dead code",
  "commit_message": "Short commit message for GitHub"
}}

Code:
```python
{code}
```
"""

def analyze_code_with_bedrock(code: str) -> Dict[str, Any]:
    """
    Analyze code using Claude 3.7 Sonnet
    
    Args:
        code (str): The code to analyze
        
    Returns:
        Dict[str, Any]: Analysis results with issue, code changes, benefit, and commit message
    """
    prompt = build_prompt(code)

    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens": 1024,
                "temperature": 0.5,
                "stop_sequences": ["\n\nHuman:"]
            })
        )

        response_body = json.loads(response["body"].read())
        model_output = response_body.get("completion")

        try:
            return json.loads(model_output)
        except json.JSONDecodeError as e:
            print("⚠️ Error parsing model output:", e)
            print("Raw output:", model_output)
            return {}
            
    except Exception as e:
        print(f"⚠️ Error analyzing code: {str(e)}")
        return {}

def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a Python file and return improvement suggestions
    
    Args:
        file_path (str): Path to the Python file to analyze
        
    Returns:
        Dict[str, Any]: Analysis results with issue, code changes, benefit, and commit message
    """
    try:
        with open(file_path, "r") as f:
            code = f.read()
        return analyze_code_with_bedrock(code)
    except Exception as e:
        print(f"⚠️ Error reading file {file_path}: {str(e)}")
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
        print(json.dumps(result, indent=2))
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file) 