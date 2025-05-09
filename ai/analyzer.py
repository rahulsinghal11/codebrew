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
        print("🔧 Sending request to Bedrock...")
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 0.5,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        print("📤 Request body:", json.dumps(request_body, indent=2))
        
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        print("📥 Received response from Bedrock")
        response_body = json.loads(response["body"].read())
        print("📦 Response body:", json.dumps(response_body, indent=2))
        
        model_output = response_body.get("content", [{}])[0].get("text", "")
        print("📝 Model output:", model_output)

        try:
            result = json.loads(model_output)
            print("✅ Successfully parsed JSON response")
            return result
        except json.JSONDecodeError as e:
            print("⚠️ Error parsing model output:", e)
            print("Raw output:", model_output)
            return {}
            
    except Exception as e:
        print(f"⚠️ Error analyzing code: {str(e)}")
        if hasattr(e, 'response'):
            print("Error response:", e.response)
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
        print(f"📂 Reading file: {file_path}")
        with open(file_path, "r") as f:
            code = f.read()
        print(f"📄 File contents:\n{code}")
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