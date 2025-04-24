from celery import shared_task
from src.utils.mailer import send_email  # use your actual email function


@shared_task
def send_verification_email_task(email: str, token: str):
    url = f"http://yourdomain.com/verify-email?token={token}"
    subject = "Verify your email"
    body = f"Click the link to verify your email:\n\n{url}"
    send_email(to=email, subject=subject, body=body)
