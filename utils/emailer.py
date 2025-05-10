import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

class Emailer:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
    
    def send_email(self, to_email: str, subject: str, body: str, 
                  is_html: bool = False) -> dict:
        """
        Send an email using SMTP
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body
            is_html (bool): Whether the body is HTML
            
        Returns:
            dict: Status of email sending
        """
        try:
            if not all([self.smtp_username, self.smtp_password]):
                raise ValueError("Email credentials not configured")
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {"status": "success", "message": "Email sent successfully"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    emailer = Emailer()
    # Test email with configured credentials
    result = emailer.send_email(
        to_email=os.getenv('SMTP_USERNAME'),  # Send to the configured email
        subject="Test Email from CodeBrew",
        body="This is a test email from CodeBrew. If you receive this, the email configuration is working correctly!",
        is_html=True
    )
    print("Email configuration:", {
        "server": emailer.smtp_server,
        "port": emailer.smtp_port,
        "username": emailer.smtp_username,
        "password_set": bool(emailer.smtp_password)
    })
    print("Send result:", result) 