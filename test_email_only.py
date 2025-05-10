import os
from dotenv import load_dotenv
from utils.emailer import Emailer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

print("\n=== Email Configuration ===")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD set: {bool(os.getenv('SMTP_PASSWORD'))}")
print(f"NOTIFICATION_EMAIL: {os.getenv('NOTIFICATION_EMAIL')}")

# Initialize emailer
emailer = Emailer()

# Send test email
print("\n=== Sending Test Email ===")
print(f"From: {os.getenv('SMTP_USERNAME')}")
print(f"To: {os.getenv('NOTIFICATION_EMAIL')}")
print("Subject: Test Email from CodeBrew - Simple Test")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_USERNAME')
    msg['To'] = os.getenv('NOTIFICATION_EMAIL')
    msg['Subject'] = "Test Email from CodeBrew - Simple Test"
    
    body = """
    <h1>Test Email</h1>
    <p>This is a simple test email to verify the email configuration.</p>
    <p>If you receive this, the email system is working correctly!</p>
    """
    msg.attach(MIMEText(body, 'html'))
    
    print("\n=== Connecting to SMTP Server ===")
    with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        print("Sending message...")
        server.send_message(msg)
        print("Message sent successfully!")
    
    print("\n=== Email Details ===")
    print("Status: Success")
    print("Message: Email sent successfully")
    
except Exception as e:
    print("\n=== Error Details ===")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}") 