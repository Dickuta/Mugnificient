import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@mugstore.com")
        self.from_name = os.getenv("FROM_NAME", "Mug Store")
        self.enabled = bool(self.smtp_user and self.smtp_password)

    def is_configured(self) -> bool:
        return self.enabled


email_config = EmailConfig()


def send_email(
    to_email: str, subject: str, html_body: str, text_body: Optional[str] = None
) -> bool:
    """
    Send an email

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content
        text_body: Plain text alternative

    Returns:
        True if sent successfully, False otherwise
    """
    if not email_config.enabled:
        logger.warning(f"Email not enabled. Would send to {to_email}: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{email_config.from_name} <{email_config.from_email}>"
        msg["To"] = to_email

        # Plain text part
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        else:
            # Strip HTML tags for plain text
            import re

            text = re.sub("<[^<]+?>", "", html_body)
            msg.attach(MIMEText(text, "plain"))

        # HTML part
        msg.attach(MIMEText(html_body, "html"))

        # Send
        with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port) as server:
            server.starttls()
            server.login(email_config.smtp_user, email_config.smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_order_confirmation(
    to_email: str,
    order_number: str,
    total: float,
    items: List[dict],
    customer_name: str,
):
    """Send order confirmation email"""
    subject = f"Order Confirmation - {order_number}"

    items_html = "".join(
        [
            f"<tr><td>{item['name']}</td><td>{item['quantity']}</td><td>${item['price']:.2f}</td></tr>"
            for item in items
        ]
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1976D2; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            .total {{ font-size: 18px; font-weight: bold; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Order Confirmed!</h1>
            </div>
            <div class="content">
                <p>Hi {customer_name},</p>
                <p>Thank you for your order! We've received your order and it's being processed.</p>
                
                <h2>Order Details</h2>
                <p><strong>Order Number:</strong> {order_number}</p>
                
                <table>
                    <thead>
                        <tr><th>Product</th><th>Qty</th><th>Price</th></tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <p class="total">Total: ${total:.2f}</p>
                
                <p>We'll notify you when your order ships.</p>
            </div>
            <div class="footer">
                <p>Mug Store - Quality Mugs for Everyone</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_order_shipped(
    to_email: str,
    order_number: str,
    tracking_number: Optional[str] = None,
    customer_name: str = "Customer",
):
    """Send order shipped notification"""
    subject = f"Your Order Has Shipped - {order_number}"

    tracking_html = (
        f"<p><strong>Tracking Number:</strong> {tracking_number}</p>"
        if tracking_number
        else ""
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Order Shipped! 📦</h1>
            </div>
            <div class="content">
                <p>Hi {customer_name},</p>
                <p>Great news! Your order has been shipped.</p>
                <p><strong>Order Number:</strong> {order_number}</p>
                {tracking_html}
                <p>Thank you for shopping with us!</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_welcome_email(to_email: str, username: str, customer_name: str = ""):
    """Send welcome email to new users"""
    subject = "Welcome to Mug Store!"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1976D2; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 10px 20px; background: #1976D2; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Mug Store! ☕</h1>
            </div>
            <div class="content">
                <p>Hi {customer_name or username},</p>
                <p>Thank you for joining Mug Store! We're excited to have you.</p>
                <p>Start browsing our collection of:</p>
                <ul>
                    <li>Classic Ceramic Mugs</li>
                    <li>Travel Mugs</li>
                    <li>Sports Bottles</li>
                    <li>Premium Gift Mugs</li>
                </ul>
                <p><a href="http://localhost:9001" class="button">Shop Now</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_password_reset(to_email: str, username: str, reset_token: str):
    """Send password reset email"""
    subject = "Password Reset - Mug Store"

    reset_link = f"http://localhost:9001/auth/reset-password?token={reset_token}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f44336; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 10px 20px; background: #1976D2; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reset Your Password</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>You requested to reset your password. Click the button below:</p>
                <p><a href="{reset_link}" class="button">Reset Password</a></p>
                <p>Or copy this link: {reset_link}</p>
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_restock_alert(to_email: str, product_name: str, current_stock: int):
    """Send restock alert to admins"""
    subject = f"Stock Alert: {product_name} is low!"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #ff9800; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Stock Alert</h1>
            </div>
            <div class="content">
                <p>The following product needs restocking:</p>
                <h2>{product_name}</h2>
                <p><strong>Current Stock:</strong> {current_stock}</p>
                <p>Please review and reorder soon.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)
