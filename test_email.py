import os
from dotenv import load_dotenv
from utils.emailer import Emailer

# Load environment variables
load_dotenv()

# Print all configurations
print("Email Configuration:")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD set: {bool(os.getenv('SMTP_PASSWORD'))}")

print("\nAWS Configuration:")
print(f"AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"AWS_ACCESS_KEY_ID set: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
print(f"AWS_SECRET_ACCESS_KEY set: {bool(os.getenv('AWS_SECRET_ACCESS_KEY'))}")

# Initialize emailer
emailer = Emailer()

# Send test email
result = emailer.send_email(
    to_email="priyanshujaiswal009@gmail.com",
    subject="Test Email from CodeBrew",
    body="<h1>Test Email</h1><p>This is a test email from CodeBrew to verify the email configuration.</p>",
    is_html=True
)

print("\nSend Result:", result) 