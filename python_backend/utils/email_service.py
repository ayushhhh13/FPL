"""Email service for sending emails via SendGrid API."""
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import SendGrid library
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️ SendGrid library not installed. Install with: pip install sendgrid")


class GmailService:
    """Service for sending emails via SendGrid API."""
    
    def __init__(self):
        # SendGrid API Configuration
        # Support both standard and Twilio-specific variable names
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", os.getenv("TWILIO_SMTP_API_KEY", ""))
        self.sender_email = os.getenv("SMTP_SENDER_EMAIL", os.getenv("TWILIO_SENDER_EMAIL", "noreply@creditcardassistant.com"))
        self.use_api = bool(self.sendgrid_api_key and SENDGRID_AVAILABLE)
        
        # Create emails directory for storing sent emails
        self.emails_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "emails")
        os.makedirs(self.emails_dir, exist_ok=True)
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> dict:
        """
        Send an email using SendGrid API or save to file.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            
        Returns:
            dict with success status and message
        """
        # Always save email to file for record keeping
        self._save_email_to_file(to_email, subject, body, is_html)
        
        if not self.use_api:
            print(f"📧 [FILE] Email saved to file (SendGrid API not configured)")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            return {
                "success": True,
                "message": f"Email saved to file (check emails/ directory). To send via SendGrid API, configure SENDGRID_API_KEY in .env",
                "to": to_email,
                "saved_to_file": True
            }
        
        try:
            # Create SendGrid message
            # SendGrid expects email addresses as strings, not Email objects for basic usage
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject
            )
            
            # Add content (HTML or plain text)
            if is_html:
                message.add_content(Content("text/html", body))
            else:
                message.add_content(Content("text/plain", body))
            
            # Send via SendGrid API
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            # Check response status
            if response.status_code in [200, 201, 202]:
                print(f"📧 [SendGrid] Email sent successfully to {to_email}")
                print(f"   Status Code: {response.status_code}")
                return {
                    "success": True,
                    "message": "Email sent successfully via SendGrid API",
                    "to": to_email,
                    "status_code": response.status_code,
                    "sent_via_api": True
                }
            else:
                error_msg = f"SendGrid returned status {response.status_code}"
                print(f"⚠️  {error_msg}")
                return {
                    "success": True,  # Still success because saved to file
                    "message": f"Email saved to file. SendGrid API returned status {response.status_code}",
                    "to": to_email,
                    "saved_to_file": True,
                    "status_code": response.status_code,
                    "api_error": error_msg
                }
        except Exception as e:
            error_str = str(e)
            print(f"❌ Error sending email via SendGrid API: {error_str}")
            
            # Provide helpful error messages
            if "403" in error_str or "Forbidden" in error_str:
                error_msg = "403 Forbidden - Check: 1) API key is valid, 2) Sender email is verified in SendGrid, 3) API key has 'Mail Send' permissions"
            elif "401" in error_str or "Unauthorized" in error_str:
                error_msg = "401 Unauthorized - API key is invalid or expired"
            else:
                error_msg = error_str
            
            return {
                "success": True,  # Still success because saved to file
                "message": f"Email saved to file. SendGrid API error: {error_msg}",
                "to": to_email,
                "saved_to_file": True,
                "api_error": error_msg
            }
    
    def _save_email_to_file(self, to_email: str, subject: str, body: str, is_html: bool):
        """Save email to a file for record keeping."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_email = to_email.replace("@", "_at_").replace(".", "_")
            filename = f"{timestamp}_{safe_email}.html" if is_html else f"{timestamp}_{safe_email}.txt"
            filepath = os.path.join(self.emails_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"{'='*50}\n\n")
                f.write(body)
            
            print(f"💾 Email saved to: {filepath}")
        except Exception as e:
            print(f"⚠️ Failed to save email to file: {str(e)}")
    
    
    def send_chat_summary(self, user_email: str, user_name: str, chat_messages: list) -> dict:
        """
        Send a chat conversation summary via email.
        
        Args:
            user_email: User's email address
            user_name: User's name
            chat_messages: List of chat messages (dict with 'role' and 'content')
            
        Returns:
            dict with success status
        """
        subject = "Credit Card Assistant - Chat Summary"
        
        # Format chat messages
        chat_html = "<div style='font-family: Arial, sans-serif; padding: 20px;'>"
        chat_html += f"<h2>Chat Conversation Summary</h2>"
        chat_html += f"<p>Dear {user_name},</p>"
        chat_html += "<p>Here is a summary of your recent conversation with the Credit Card Assistant:</p>"
        chat_html += "<div style='background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;'>"
        
        for msg in chat_messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                chat_html += f"<p><strong>You:</strong> {content}</p>"
            else:
                chat_html += f"<p><strong>Assistant:</strong> {content}</p>"
        
        chat_html += "</div>"
        chat_html += "<p>Thank you for using our Credit Card Assistant!</p>"
        chat_html += "</div>"
        
        return self.send_email(user_email, subject, chat_html, is_html=True)
