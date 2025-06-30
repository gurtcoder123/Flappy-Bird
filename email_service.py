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
            # Validate configuration
            if not self.email_address or self.email_address == "noreply@flappybird.com":
                print(f"Email Error: EMAIL_ADDRESS not configured properly")
                return False
            
            if not self.email_password or self.email_password == "default_password":
                print(f"Email Error: EMAIL_PASSWORD not configured properly")
                return False
            
            print(f"Attempting to send email from {self.email_address} to {to_email}")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server with detailed logging
            print(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.set_debuglevel(1)  # Enable SMTP debugging
            
            print("Starting TLS encryption...")
            server.starttls()
            
            print("Attempting SMTP login...")
            server.login(self.email_address, self.email_password)
            
            print("Sending email...")
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {str(e)}")
            print("Check that EMAIL_ADDRESS and EMAIL_PASSWORD are correct")
            print("For Gmail, use an App Password, not your regular password")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {str(e)}")
            return False
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            print(f"Email config: server={self.smtp_server}, port={self.smtp_port}")
            return False
