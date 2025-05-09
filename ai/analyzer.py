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
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Initialize Bedrock client
client = boto3.client("bedrock-runtime", region_name=region)

def build_prompt(code: str) -> str:
    """Build the prompt for Claude with the code to analyze"""
    return f"""You are a senior Python engineer specializing in performance optimization and code quality.

Review the following code file and identify the single most impactful improvement that would provide at least 20% performance gain or significant maintainability improvement.

Focus on:
1. Performance bottlenecks (time complexity, memory usage)
2. Critical bugs or edge cases
3. Major architectural improvements
4. Security vulnerabilities

Return a valid JSON object with these fields:
{{
    "issue": "A clear, concise explanation of the problem (max 2 sentences)",
    "old_code": "The original code block with line numbers",
    "new_code": "The improved code with line numbers",
    "benefit": {{
        "performance_gain": "Estimated performance improvement (e.g., '40% faster', '50% less memory')",
        "complexity_before": "Time/space complexity before (e.g., 'O(n²)', 'O(n) space')",
        "complexity_after": "Time/space complexity after (e.g., 'O(n log n)', 'O(1) space')",
        "explanation": "Detailed explanation of why this improvement matters"
    }},
    "commit_message": "A clear, concise commit message (max 50 chars)",
    "email_template": {{
        "subject": "Code Improvement Suggestion: [Brief Description]",
        "body": "A well-formatted email body with sections for the issue, before/after code, and benefits"
    }}
}}

Code to review:
```python
{code}
```

Important:
- Only suggest changes with at least 20% performance improvement or significant maintainability impact
- Include specific metrics and complexity analysis
- Make the email template clear and actionable
- Focus on one major improvement rather than multiple small changes
- Ensure the response is valid JSON without any markdown formatting
"""

def clean_json_string(text: str) -> str:
    """Clean JSON string by removing markdown code block markers"""
    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
    if text.endswith("```"):
        text = text.replace("```", "", 1)
    return text.strip()

def analyze_code_with_bedrock(code: str) -> Dict[str, Any]:
    """
    Analyze code using Claude 3 Sonnet
    
    Args:
        code (str): The code to analyze
        
    Returns:
        Dict[str, Any]: Analysis results with issue, code changes, benefit, and commit message
    """
    prompt = build_prompt(code)

    try:
        print("🔍 Analyzing code...")
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
        
        print("📤 Sending request to Bedrock...")
        
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        print("📥 Received response from Bedrock")
        response_body = json.loads(response["body"].read())
        
        model_output = response_body.get("content", [{}])[0].get("text", "")
        print("\n📝 AI Suggestion:")

        try:
            # Clean the JSON string before parsing
            cleaned_output = clean_json_string(model_output)
            result = json.loads(cleaned_output)
            
            # Print formatted suggestion
            print("\n🔍 Issue Found:")
            print(result["issue"])
            print("\n📄 Original Code:")
            print(result["old_code"])
            print("\n✨ Improved Code:")
            print(result["new_code"])
            print("\n📈 Performance Analysis:")
            print(f"• Performance Gain: {result['benefit']['performance_gain']}")
            print(f"• Complexity Before: {result['benefit']['complexity_before']}")
            print(f"• Complexity After: {result['benefit']['complexity_after']}")
            print(f"• Explanation: {result['benefit']['explanation']}")
            print("\n💬 Commit Message:")
            print(result["commit_message"])
            print("\n📧 Email Template:")
            print(f"Subject: {result['email_template']['subject']}")
            print("\nBody:")
            print(result["email_template"]["body"])
            
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