class AppException(Exception):
    def __init__(self, status_code: int, sender: str, detail: str = None):
        self.status_code = status_code
        self.sender = sender
        self.detail = detail
