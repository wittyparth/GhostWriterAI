"""
Email Service using SMTP (Brevo or generic).

Handles sending transactional emails like verification, password reset, etc.
Using standard smtplib run in threadpool for non-blocking async execution.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from starlette.concurrency import run_in_threadpool

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        settings = get_settings()
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password.get_secret_value() if settings.smtp_password else None
        self.from_email = settings.from_email
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not found. Email service disabled.")

    def _send_sync(self, to_email: str, subject: str, html_content: str):
        """
        Synchronous SMTP send function.
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning(f"Email service disabled. Would have sent to {to_email}")
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(html_content, "html"))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent to {to_email} via SMTP")
            return {"status": "success", "message": "Email sent"}
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise e

    async def send_verification_email(self, to_email: str, name: str, token: str, frontend_url: str):
        """
        Send verification email to user using SMTP (Async wrapper).
        """
        verification_link = f"{frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #2563EB; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    font-weight: bold;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome to LinkedIn AI Agent!</h2>
                <p>Hi {name},</p>
                <p>Thanks for signing up. Please verify your email address to get started.</p>
                <p>
                    <a href="{verification_link}" class="button">Verify Email</a>
                </p>
                <p>Or verify using this link: <a href="{verification_link}">{verification_link}</a></p>
                <p>This link will expire in 24 hours.</p>
                
                <div class="footer">
                    <p>If you didn't create an account, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Run blocking SMTP call in a separate thread
        return await run_in_threadpool(
            self._send_sync,
            to_email,
            "Verify your email address",
            html_content
        )
