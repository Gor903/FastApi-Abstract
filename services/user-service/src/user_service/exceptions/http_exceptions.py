from .base import AppException


class RecordCreate(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="DB create service", detail=detail)


class RecordRead(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="DB read service", detail=detail)


class RecordUpdate(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="DB update service", detail=detail)


class RecordDelete(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="DB delete service", detail=detail)


class NoAuthException(AppException):
    def __init__(self, sender: str, detail: str = None):
        super().__init__(status_code=400, sender=sender, detail=detail)


class JWTException(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="JWT worker service", detail=detail)


class ValidationException(AppException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, sender="validation service", detail=detail)


class CTRLException(AppException):
    def __init__(self, detail: str, sender: str = "Controllers"):
        super().__init__(status_code=400, sender=sender, detail=detail)


class HTTPXException(AppException):
    def __init__(self, sender: str, detail: str):
        super().__init__(status_code=400, sender=sender, detail=detail)
