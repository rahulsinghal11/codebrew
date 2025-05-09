import boto3
import json
from pathlib import Path
import os
from dotenv import load_dotenv

def get_bedrock_client():
    """Get a configured Bedrock client"""
    load_dotenv()
    return boto3.client(
        "bedrock-runtime",
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

def load_file(file_path):
    """Load and return the contents of a Python file"""
    with open(file_path, "r") as f:
        return f.read()

def build_prompt(code):
    """Build the prompt for Claude with the code to analyze"""
    return f"""
You are a senior AI code reviewer.

Analyze the following Python code and identify the single most meaningful change that would improve performance, readability, or maintainability.

Return your answer as JSON in the following format:
{{
  "issue": "What needs to be improved",
  "old_code": "the original code block",
  "new_code": "the improved version",
  "benefit": "e.g. 30% speedup, cleaner, or removes dead code",
  "commit_message": "Short commit message for GitHub"
}}

Code:

{code}

"""

def analyze_python_file(file_path):
    """
    Analyze a Python file and return improvement suggestions
    
    Args:
        file_path (str): Path to the Python file to analyze
        
    Returns:
        dict: Analysis results with issue, code changes, benefit, and commit message
    """
    code = load_file(file_path)
    prompt = build_prompt(code)
    client = get_bedrock_client()

    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 1000,
                "temperature": 0.5,
                "stop_sequences": ["\n\nHuman:"]
            })
        )

        response_body = json.loads(response['body'].read())
        model_output = response_body['completion']

        try:
            suggestion = json.loads(model_output)
            return suggestion
        except json.JSONDecodeError:
            print("Failed to parse model response. Here is raw output:\n", model_output)
            return None
            
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
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
        result = analyze_python_file(test_file)
        print(json.dumps(result, indent=2))
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file) 