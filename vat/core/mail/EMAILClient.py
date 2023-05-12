# -*- coding:utf-8 -*-
"""
author: ZHU JIN
date: 2022.11.14
description: (0_0)
"""
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger


class EmailClient:
    def __init__(self, sender: str, username: str, password: str) -> None:
        self._mail_server = "rb-smtp-int.bosch.com"
        self._mail_server_port = 25
        self._sender = sender
        self._credentials = {"username": username, "password": password}

    def send_mail(self, recipients: list, subject: str, email_body: str) -> None:
        msg = MIMEMultipart()
        body = MIMEText(email_body, "html")
        # body = MIMEText(email_body)
        msg["Subject"] = subject
        msg.attach(body)
        msg["From"] = self._sender
        msg["To"] = ", ".join(recipients)

        with SMTP(self._mail_server, port=self._mail_server_port) as conn:
            conn.login(self._credentials["username"], self._credentials["password"])
            logger.success("Login successfully!")
            conn.sendmail(self._sender, recipients, msg.as_string())
            logger.success("Mail sent successfully!")
