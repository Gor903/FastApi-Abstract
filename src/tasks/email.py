from celery import shared_task

from src.core import settings
from src.utils import send_email


@shared_task
def send_verification_email_task(email: str, token: str):
    url = f"http://{settings.DOMAIN_NAME}/auth/verify_email?token={token}"
    subject = "Verify your email"
    body = f"Click the link to verify your email:\n\n{url}"
    send_email(to=email, subject=subject, body=body)
