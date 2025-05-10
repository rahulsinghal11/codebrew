import boto3
import json
from dotenv import load_dotenv
import os

def test_aws_bedrock():
    # Load environment variables
    load_dotenv()
    
    # Configuration
    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    try:
        print("Initializing Bedrock client...")
        client = boto3.client("bedrock-runtime", region_name=region)
        
        print("\nTesting Bedrock connection...")
        # Simple test prompt
        prompt = "Hello, can you respond with a simple 'Hello World'?"
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        print("Sending request to Bedrock...")
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        print("Received response from Bedrock")
        response_body = json.loads(response['body'].read())
        print("\nResponse:", response_body['content'][0]['text'])
        
    except Exception as e:
        print(f"Error testing AWS Bedrock: {str(e)}")
        if hasattr(e, 'response'):
            print("Error response:", e.response)

if __name__ == "__main__":
    test_aws_bedrock()
