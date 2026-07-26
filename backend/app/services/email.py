"""
Email service for sending notifications.
Uses SMTP (can be configured for SendGrid, Resend, etc.).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "support@smart-support.com")


def send_reply_email(to_email: str, customer_name: str, reply: str, ticket_id: int) -> bool:
    """
    Send a reply email to a customer.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP credentials not set. Email not sent.")
        return False
    
    subject = f"Re: Support Ticket #{ticket_id}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>Thank you for contacting support. Here's our response to your ticket:</p>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
            {reply}
        </div>
        <p>If you have any further questions, feel free to reply to this email.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
        <p style="font-size: 12px; color: #888;">
            Ticket #{ticket_id} | Smart Support System
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = to_email
    
    part = MIMEText(html_body, 'html')
    msg.attach(part)
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_ticket_created_email(to_email: str, customer_name: str, ticket_id: int) -> bool:
    """
    Send confirmation email when a ticket is created.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP credentials not set. Email not sent.")
        return False
    
    subject = f"Support Ticket #{ticket_id} Received"
    
    html_body = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>We have received your support ticket <strong>#{ticket_id}</strong>.</p>
        <p>Our team will review it and get back to you as soon as possible.</p>
        <p>You can expect a response within 24 hours.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
        <p style="font-size: 12px; color: #888;">
            Ticket #{ticket_id} | Smart Support System
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = to_email
    
    part = MIMEText(html_body, 'html')
    msg.attach(part)
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Ticket confirmation email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_ticket_resolved_email(to_email: str, customer_name: str, ticket_id: int) -> bool:
    """
    Send notification when a ticket is resolved.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP credentials not set. Email not sent.")
        return False
    
    subject = f"Support Ticket #{ticket_id} Resolved"
    
    html_body = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>We are happy to inform you that your support ticket <strong>#{ticket_id}</strong> has been resolved.</p>
        <p>If you're satisfied with the resolution, you don't need to do anything.</p>
        <p>If you're still experiencing issues, please reply to this email and we'll reopen the ticket.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
        <p style="font-size: 12px; color: #888;">
            Ticket #{ticket_id} | Smart Support System
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = to_email
    
    part = MIMEText(html_body, 'html')
    msg.attach(part)
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Resolution email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False