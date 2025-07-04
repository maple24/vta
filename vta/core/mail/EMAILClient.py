# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

# -*- coding:utf-8 -*-
"""
Email client module for sending emails via SMTP.

Author: ZHU JIN
Date: 2022.11.14
Description: Robust email client with proper error handling and validation
"""

import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPException, SMTPAuthenticationError, SMTPConnectError
from typing import List, Optional

from loguru import logger


class EmailClientError(Exception):
    """Custom exception for EmailClient errors."""

    pass


class EmailClient:
    """
    A robust email client for sending emails via SMTP.

    Attributes:
        DEFAULT_SERVER (str): Default SMTP server
        DEFAULT_PORT (int): Default SMTP port
    """

    DEFAULT_SERVER = "smtp.app.bosch.com"
    DEFAULT_PORT = 25
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(
        self,
        sender: str,
        username: str,
        password: str,
        mail_server: Optional[str] = None,
        mail_server_port: Optional[int] = None,
    ) -> None:
        """
        Initialize the EmailClient.

        Args:
            sender: Email address of the sender
            username: SMTP username for authentication
            password: SMTP password for authentication
            mail_server: SMTP server address (optional, uses default if not provided)
            mail_server_port: SMTP server port (optional, uses default if not provided)

        Raises:
            EmailClientError: If sender email is invalid or credentials are empty
        """
        self._validate_email(sender, "sender")
        self._validate_credentials(username, password)

        self._mail_server = mail_server or self.DEFAULT_SERVER
        self._mail_server_port = mail_server_port or self.DEFAULT_PORT
        self._sender = sender
        self._credentials = {"username": username, "password": password}

        logger.info(f"EmailClient initialized for sender: {sender}")

    def send_mail(self, recipients: List[str], subject: str, email_body: str, content_type: str = "html") -> bool:
        """
        Send an email to the specified recipients.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject line
            email_body: Email body content
            content_type: Content type for email body ("html" or "plain")

        Returns:
            bool: True if email was sent successfully, False otherwise

        Raises:
            EmailClientError: If input validation fails or email sending fails
        """
        try:
            self._validate_send_mail_inputs(recipients, subject, email_body, content_type)

            msg = self._create_message(recipients, subject, email_body, content_type)
            self._send_message(msg, recipients)

            logger.success(f"Email sent successfully to {len(recipients)} recipients")
            return True

        except (SMTPAuthenticationError, SMTPConnectError, SMTPException) as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            logger.error(error_msg)
            raise EmailClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            raise EmailClientError(error_msg) from e

    def _validate_email(self, email: str, field_name: str) -> None:
        """Validate email address format."""
        if not email or not isinstance(email, str):
            raise EmailClientError(f"{field_name} email cannot be empty")

        if not self.EMAIL_PATTERN.match(email):
            raise EmailClientError(f"Invalid {field_name} email format: {email}")

    def _validate_credentials(self, username: str, password: str) -> None:
        """Validate SMTP credentials."""
        if not username or not isinstance(username, str):
            raise EmailClientError("Username cannot be empty")

        if not password or not isinstance(password, str):
            raise EmailClientError("Password cannot be empty")

    def _validate_send_mail_inputs(
        self, recipients: List[str], subject: str, email_body: str, content_type: str
    ) -> None:
        """Validate inputs for send_mail method."""
        if not recipients or not isinstance(recipients, list):
            raise EmailClientError("Recipients list cannot be empty")

        for recipient in recipients:
            self._validate_email(recipient, "recipient")

        if not subject or not isinstance(subject, str):
            raise EmailClientError("Subject cannot be empty")

        if not isinstance(email_body, str):
            raise EmailClientError("Email body must be a string")

        if content_type not in ["html", "plain"]:
            raise EmailClientError("Content type must be either 'html' or 'plain'")

    def _create_message(self, recipients: List[str], subject: str, email_body: str, content_type: str) -> MIMEMultipart:
        """Create email message."""
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self._sender
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(email_body, content_type))
        return msg

    def _send_message(self, msg: MIMEMultipart, recipients: List[str]) -> None:
        """Send the email message via SMTP."""
        logger.info(f"Connecting to SMTP server: {self._mail_server}:{self._mail_server_port}")

        with SMTP(self._mail_server, port=self._mail_server_port) as conn:
            conn.ehlo()
            conn.starttls()
            conn.ehlo()

            logger.info("Authenticating with SMTP server")
            conn.login(self._credentials["username"], self._credentials["password"])
            logger.success("SMTP authentication successful")

            conn.sendmail(self._sender, recipients, msg.as_string())
            logger.info(f"Email sent to: {', '.join(recipients)}")


# Example usage (remove in production)
if __name__ == "__main__":
    try:
        email_client = EmailClient(sender="Test.EST@cn.bosch.com", username="ets1szh", password="estbangbangde-")
        recipients = ["jin.zhu5@cn.bosch.com"]
        success = email_client.send_mail(
            recipients=recipients, subject="Test Email", email_body="<h1>Test Message</h1><p>This is a test email.</p>"
        )

        if success:
            logger.info("Email operation completed successfully")

    except EmailClientError as e:
        logger.error(f"Email client error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
