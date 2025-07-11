from .base import AppException


class GatewayException(AppException):
    def __init__(self, service_name: str, detail: str = None):
        super().__init__(status_code=400, service_name=service_name, detail=detail)
