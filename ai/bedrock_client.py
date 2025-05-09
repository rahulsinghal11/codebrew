import boto3
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from dotenv import load_dotenv

class BedrockClient:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
        
    def generate_text(self, prompt: str) -> Optional[Dict]:
        """Generate text using AWS Bedrock"""
        try:
            response = self.client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                })
            )
            
            response_body = json.loads(response.get('body').read())
            content = response_body.get('content', [{}])[0].get('text', '{}')
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"issue": content}
            
        except Exception as e:
            print(f"Error generating text with Bedrock: {str(e)}")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code using Claude
        
        Args:
            code (str): Code to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        prompt = f"""You are an AI code reviewer. Analyze the following Python code and suggest one important improvement. 
        Focus on:
        1. Code quality and readability
        2. Performance optimization
        3. Security considerations
        4. Best practices
        
        Return your analysis in this JSON format:
        {{
            "issue": "Description of the issue found",
            "benefit": {{
                "explanation": "How this optimization helps",
                "impact": "High/Medium/Low"
            }},
            "suggestion": "Specific code suggestion"
        }}
        
        Here's the code to analyze:
        
        {code}"""
        
        return self.generate_text(prompt)

    def analyze_structured_data(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Analyze structured data using AWS Bedrock"""
        try:
            # Convert the structured data to a clear prompt
            prompt = f"""You are an expert code reviewer. Analyze this repository and its files to suggest optimizations.

Repository Information:
{json.dumps(data['repository'], indent=2)}

Files to Analyze:
{json.dumps(data['files'], indent=2)}

Analysis Requirements:
{json.dumps(data['analysis_requirements'], indent=2)}

Please analyze each file and provide suggestions in this exact format:
{{
    "analyses": [
        {{
            "file": "string (file path)",
            "issue": "string (description of the issue)",
            "benefit": {{
                "explanation": "string (how this optimization helps)",
                "impact": "string (High/Medium/Low)"
            }},
            "suggestion": "string (specific code suggestion)"
        }},
        // ... more analyses for other files
    ]
}}

Focus on the relationships between files and how they can be optimized together. Provide at least one analysis per file."""

            response = self.client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 4000,  # Increased for multiple file analysis
                    "temperature": 0.7
                })
            )
            
            response_body = json.loads(response.get('body').read())
            content = response_body.get('content', [{}])[0].get('text', '{}')
            
            # If content is already a dict, return it
            if isinstance(content, dict):
                return content
                
            # Try to parse as JSON string
            try:
                # Clean up the content string
                if isinstance(content, str):
                    # Find the first occurrence of a JSON object
                    start_idx = content.find('{')
                    if start_idx == -1:
                        raise json.JSONDecodeError("No JSON object found", content, 0)
                    
                    # Find the matching closing brace
                    brace_count = 0
                    end_idx = -1
                    for i in range(start_idx, len(content)):
                        if content[i] == '{':
                            brace_count += 1
                        elif content[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx == -1:
                        raise json.JSONDecodeError("No matching closing brace found", content, len(content))
                    
                    # Extract just the JSON part
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
                    
            except json.JSONDecodeError as e:
                import traceback
                print(f"Error parsing response as JSON:")
                print(traceback.format_exc())
                print("\nRaw response:")
                print(content)
                return None
            
        except Exception as e:
            import traceback
            print(f"Error analyzing structured data with Bedrock:")
            print(traceback.format_exc())
            return None

if __name__ == "__main__":
    # Example usage
    client = BedrockClient()
    sample_code = """
    def calculate_factorial(n):
        if n == 0:
            return 1
        return n * calculate_factorial(n-1)
    """
    result = client.analyze_code(sample_code)
    print(json.dumps(result, indent=2)) 