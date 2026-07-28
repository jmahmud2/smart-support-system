"""
Email service for sending notifications using Resend API.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "support@smart-support.com")


def send_reply_email(to_email: str, customer_name: str, reply: str, ticket_id: int) -> bool:
    """Send a reply email to a customer using Resend."""
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set. Email not sent.")
        return False

    subject = f"Re: Support Ticket #{ticket_id}"

    html_content = f"""
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

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=15.0,
        )

        if response.status_code == 200:
            print(f"Email sent to {to_email}")
            return True
        else:
            print(f"Email failed: {response.text}")
            return False

    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_ticket_created_email(to_email: str, customer_name: str, ticket_id: int) -> bool:
    """Send confirmation email when a ticket is created."""
    if not RESEND_API_KEY:
        return False

    subject = f"Support Ticket #{ticket_id} Received"

    html_content = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>We have received your support ticket <strong>#{ticket_id}</strong>.</p>
        <p>Our team will review it and get back to you as soon as possible.</p>
        <p>You can expect a response within 24 hours.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
    </body>
    </html>
    """

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=15.0,
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_ticket_resolved_email(to_email: str, customer_name: str, ticket_id: int) -> bool:
    """Send notification when a ticket is resolved."""
    if not RESEND_API_KEY:
        return False

    subject = f"Support Ticket #{ticket_id} Resolved"

    html_content = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>We are happy to inform you that your support ticket <strong>#{ticket_id}</strong> has been resolved.</p>
        <p>If you're satisfied, you don't need to do anything.</p>
        <p>If you're still experiencing issues, reply to this email and we'll reopen the ticket.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
    </body>
    </html>
    """

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=15.0,
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_assignment_email(to_email: str, customer_name: str, ticket_id: int, agent_name: str) -> bool:
    """Send notification when a ticket is assigned to an agent."""
    if not RESEND_API_KEY:
        return False

    subject = f"Your Ticket #{ticket_id} Has Been Assigned"

    html_content = f"""
    <html>
    <body>
        <h2>Hello {customer_name or 'there'},</h2>
        <p>Your support ticket <strong>#{ticket_id}</strong> has been assigned to <strong>{agent_name}</strong>.</p>
        <p>Our agent will review your case and get back to you shortly.</p>
        <p>You can track your ticket status here:</p>
        <a href="https://yourdomain.com/customer/track">Track Your Ticket</a>
        <br>
        <p>Best regards,<br>Support Team</p>
    </body>
    </html>
    """

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=15.0,
        )

        if response.status_code == 200:
            print(f"Assignment email sent to {to_email}")
            return True
        else:
            print(f"Assignment email failed: {response.text}")
            return False

    except Exception as e:
        print(f"Assignment email error: {e}")
        return False


def send_agent_assignment_notification(to_email: str, agent_name: str, ticket_id: int, customer_name: str) -> bool:
    """Send notification to agent when a ticket is assigned to them."""
    if not RESEND_API_KEY:
        return False

    subject = f"New Ticket #{ticket_id} Assigned to You"

    html_content = f"""
    <html>
    <body>
        <h2>Hello {agent_name},</h2>
        <p>A new ticket <strong>#{ticket_id}</strong> has been assigned to you.</p>
        <p><strong>Customer:</strong> {customer_name or 'Anonymous'}</p>
        <p>Please log in to the support dashboard to view and respond to this ticket.</p>
        <br>
        <p>Best regards,<br>Support Team</p>
    </body>
    </html>
    """

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=15.0,
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Agent notification email error: {e}")
        return False