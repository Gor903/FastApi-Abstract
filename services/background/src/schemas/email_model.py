from pydantic import BaseModel, EmailStr


class EmailSendData(BaseModel):
    to: EmailStr
    subject: str
    body: str
