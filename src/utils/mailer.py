import smtplib
from email.message import EmailMessage

from core import settings


def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = to
    msg.set_content(body)

    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
