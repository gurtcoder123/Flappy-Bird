import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from settings import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
    
    def send_verification_email(self, to_email, username, verification_token):
        """Send verification email to new user"""
        subject = "Jumpy Bird - Verify Your Email"
        
        body = f"""
        Hi {username},
        
        Welcome to Jumpy Bird! Please click the link below to verify your email address:
        
        Verification Token: {verification_token}
        
        (Note: In a real application, this would be a clickable link)
        
        Thanks for joining!
        The Jumpy Bird Team
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_password_reset_email(self, to_email, reset_token):
        """Send password reset email"""
        subject = "Jumpy Bird - Password Reset"
        
        body = f"""
        Hi,
        
        You requested a password reset for your Jumpy Bird account.
        
        Reset Token: {reset_token}
        
        (Note: In a real application, this would be a clickable link)
        
        If you didn't request this, please ignore this email.
        
        The Jumpy Bird Team
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
