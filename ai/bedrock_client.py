import boto3
import json
from typing import Dict, Any, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

class BedrockClient:
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize the Bedrock client
        
        Args:
            region_name (str): AWS region name
        """
        load_dotenv()
        self.region_name = region_name
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    
    def invoke_claude(self, prompt: str, code: str, 
                     max_tokens: int = 1000, 
                     temperature: float = 0.5) -> Dict[str, Any]:
        """
        Invoke Claude 3 Sonnet model
        
        Args:
            prompt (str): The prompt to send to Claude
            code (str): The code to analyze
            max_tokens (int): Maximum tokens in response
            temperature (float): Response temperature (0.0 to 1.0)
            
        Returns:
            Dict[str, Any]: Model response
        """
        try:
            response = self.client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "prompt": f"{prompt}\n\n{code}",
                    "max_tokens_to_sample": max_tokens,
                    "temperature": temperature
                })
            )
            
            return json.loads(response['body'].read())
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code using Claude
        
        Args:
            code (str): Code to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        prompt = """You are an AI code reviewer. Analyze the following Python code and suggest one important improvement. 
        Focus on:
        1. Code quality and readability
        2. Performance optimization
        3. Security considerations
        4. Best practices
        
        Provide your analysis in a structured format."""
        
        return self.invoke_claude(prompt, code)

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