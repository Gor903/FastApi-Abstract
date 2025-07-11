from fastapi import APIRouter
from pydantic import EmailStr
from src.schemas.email_model import EmailSendData
from src.tasks import send_email_task
from starlette import status

router = APIRouter(
    prefix="/notification",
    tags=["Notification"],
)


@router.post(
    path="/mail",
    status_code=status.HTTP_200_OK,
)
async def send_mail(data: EmailSendData):
    to: EmailStr = data.to
    subject: str = data.subject
    body: str = data.body

    send_email_task.delay(email=to, subject=subject, body=body)
