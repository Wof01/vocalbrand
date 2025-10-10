"""Email utilities for VocalBrand contact form."""
from __future__ import annotations
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple


def send_contact_email(name: str, email: str, subject: str, message: str) -> Tuple[bool, str]:
    """Send contact form email via SMTP.
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
    
    Returns:
        Tuple of (success, message)
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM_EMAIL", smtp_username)
    support_email = os.getenv("SUPPORT_EMAIL", smtp_username)
    
    # Validate configuration
    if not all([smtp_host, smtp_username, smtp_password]):
        return False, "Email not configured. Please contact support directly."
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_from
        msg["To"] = support_email
        msg["Subject"] = f"VocalBrand Contact: {subject}"
        msg["Reply-To"] = email
        
        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2c3e50;">New Contact Form Submission</h2>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>From:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <p><strong>Subject:</strong> {subject}</p>
                </div>
                
                <div style="background: #ffffff; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Message:</h3>
                    <p style="white-space: pre-wrap;">{message}</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="color: #7f8c8d; font-size: 12px;">
                    This email was sent from the VocalBrand contact form.<br>
                    Reply directly to this email to respond to {name}.
                </p>
            </body>
        </html>
        """
        
        # Plain text version (fallback)
        text_body = f"""
New Contact Form Submission

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Reply to: {email}
        """
        
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, "Message sent successfully! We'll get back to you soon."
    
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please try again later."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def is_email_configured() -> bool:
    """Check if email is properly configured."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    return bool(smtp_host and smtp_username and smtp_password)
