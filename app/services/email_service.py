import aiosmtplib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from pathlib import Path

from app.core.config import settings
from app.core.logger import logger


class EmailService:
    """Email service for sending emails via SMTP"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        
        if not settings.SEND_EMAIL_ENABLED:
            logger.warning(f"Email sending is disabled. Would send to: {to_email}")
            logger.debug(f"Subject: {subject}")
            logger.debug(f"Content: {text_content or html_content}")
            return True
        
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email - Gmail için smtplib kullan
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_otp_email(to_email: str, otp_code: str, purpose: str = "registration") -> bool:
        """Send OTP code via email"""
        
        purpose_text = {
            "registration": "Registration",
            "password_reset": "Password Reset",
            "login": "Login Verification",
            "email_verification": "Email Verification"
        }.get(purpose, "Verification")
        
        subject = f"{settings.APP_NAME} - {purpose_text} OTP Code"
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    text-align: center;
                    padding: 20px;
                    background-color: #fff;
                    border: 2px dashed #4CAF50;
                    border-radius: 5px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .warning {{
                    color: #f44336;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.APP_NAME}</h1>
                </div>
                <div class="content">
                    <h2>Your {purpose_text} OTP Code</h2>
                    <p>Hello,</p>
                    <p>You have requested a one-time password (OTP) for {purpose_text.lower()}.</p>
                    <p>Your OTP code is:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p><strong>This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</strong></p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <p class="warning">⚠️ Never share this code with anyone. Our team will never ask for your OTP code.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from {settings.APP_NAME}. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text content
        text_content = f"""
        {settings.APP_NAME} - {purpose_text} OTP Code
        
        Hello,
        
        You have requested a one-time password (OTP) for {purpose_text.lower()}.
        
        Your OTP code is: {otp_code}
        
        This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.
        
        If you didn't request this code, please ignore this email.
        
        ⚠️ Never share this code with anyone. Our team will never ask for your OTP code.
        
        ---
        This is an automated message from {settings.APP_NAME}. Please do not reply to this email.
        """
        
        return await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    async def send_welcome_email(to_email: str, username: str) -> bool:
        """Send welcome email to new user"""
        
        subject = f"Welcome to {settings.APP_NAME}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {settings.APP_NAME}! 🎉</h1>
                </div>
                <div class="content">
                    <h2>Hello {username}!</h2>
                    <p>Thank you for registering with {settings.APP_NAME}.</p>
                    <p>Your account has been successfully created and verified.</p>
                    <p>You can now log in and start using our services.</p>
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The {settings.APP_NAME} Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {settings.APP_NAME}!
        
        Hello {username}!
        
        Thank you for registering with {settings.APP_NAME}.
        
        Your account has been successfully created and verified.
        
        You can now log in and start using our services.
        
        If you have any questions or need assistance, please don't hesitate to contact our support team.
        
        Best regards,
        The {settings.APP_NAME} Team
        """
        
        return await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
