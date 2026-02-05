"""
Email service for sending digest emails.
"""

import json
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from spider_aggregation.config import get_config
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EmailResult:
    """Result of email sending."""

    success: bool
    message: str
    error: Optional[str] = None


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_address: Optional[str] = None,
    ):
        """Initialize email service.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS encryption
            from_address: From email address (defaults to username)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_address = from_address or username

    def send_email(
        self,
        to_addresses: list[str],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
    ) -> EmailResult:
        """Send an email.

        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body_text: Plain text body (optional)
            body_html: HTML body (optional)

        Returns:
            EmailResult indicating success or failure
        """
        if not to_addresses:
            return EmailResult(success=False, error="No recipients specified")

        if not body_text and not body_html:
            return EmailResult(success=False, error="No email body provided")

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = ", ".join(to_addresses)

        # Add body parts
        if body_text:
            msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))

        try:
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(self.username, self.password)
                server.sendmail(self.from_address, to_addresses, msg.as_string())

            logger.info(f"Email sent successfully to {len(to_addresses)} recipients")
            return EmailResult(success=True, message=f"Email sent to {', '.join(to_addresses)}")

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, error=error_msg)

    def test_connection(self) -> EmailResult:
        """Test SMTP connection.

        Returns:
            EmailResult indicating connection success
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(self.username, self.password)
                return EmailResult(success=True, message="SMTP connection successful")
        except Exception as e:
            return EmailResult(success=False, error=str(e))


def create_email_service(
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_tls: Optional[bool] = None,
    from_address: Optional[str] = None,
) -> EmailService:
    """Factory function to create EmailService from config.

    Args:
        smtp_host: SMTP host (defaults to config)
        smtp_port: SMTP port (defaults to config)
        username: Username (defaults to config)
        password: Password (defaults to config)
        use_tls: Use TLS (defaults to config)
        from_address: From address (defaults to config)

    Returns:
        Configured EmailService
    """
    config = get_config()
    email_config = config.email

    return EmailService(
        smtp_host=smtp_host or email_config.smtp_host,
        smtp_port=smtp_port or email_config.smtp_port,
        username=username or email_config.username,
        password=password or email_config.password,
        use_tls=use_tls if use_tls is not None else email_config.use_tls,
        from_address=from_address or email_config.from_address,
    )
