"""
Email service for sending notifications.
Uses Resend API (free tier).
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "support@yourdomain.com")


def send_reply_email(to_email: str, customer_name: str, reply: str, ticket_id: int):
    """
    Send a reply email to a customer.
    """
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set. Email not sent.")
        return False

    subject = f"Re: Support Ticket #{ticket_id}"

    html_content = f"""
    <h2>Hello {customer_name or 'there'},</h2>
    <p>Thank you for contacting support. Here's our response to your ticket:</p>
    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
        {reply}
    </div>
    <p>If you have any further questions, feel free to reply to this email.</p>
    <br>
    <p>Best regards,<br>Support Team</p>
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
            print(f" Email failed: {response.text}")
            return False

    except Exception as e:
        print(f" Email error: {e}")
        return False