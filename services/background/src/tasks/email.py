from celery import shared_task
from src.utils import send_email


@shared_task(name="src.tasks.email.send_email_task")
def send_email_task(email: str, subject: str, body: str):
    send_email(to=email, subject=subject, body=body)
