class AppException(Exception):
    def __init__(self, status_code: int, service_name: str, detail: str = None):
        self.status_code = status_code
        self.service_name = service_name
        self.detail = detail
