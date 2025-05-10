import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print AWS configuration
print("AWS Configuration:")
print(f"AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")
print(f"AWS_SECRET_ACCESS_KEY set: {bool(os.getenv('AWS_SECRET_ACCESS_KEY'))}")

try:
    # Initialize Bedrock client
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    # Try a simple model invocation
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 0.1,
            "messages": [{
                "role": "user",
                "content": "Say hello!"
            }]
        })
    )
    
    response_body = json.loads(response['body'].read())
    print("\nModel Response:")
    print(response_body['content'][0]['text'])
        
except Exception as e:
    print(f"\nError: {str(e)}") 