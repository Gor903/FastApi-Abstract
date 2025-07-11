from exceptions.http_exceptions import ValidationException


def password_validator(password: str):
    if not 7 < len(password) < 16:
        raise ValidationException(
            detail="Password must be between 8 and 15 characters",
        )
    if not any(char.isdigit() for char in password):
        raise ValidationException(
            detail="Password must contain at least 1 number",
        )
    if not any(char.isalpha() for char in password):
        raise ValidationException(
            detail="Password must contain at least 1 letter",
        )
    if not any(char.isupper() for char in password):
        raise ValidationException(
            detail="Password must contain at least 1 uppercase letter",
        )
    if all(char.isalnum() for char in password):
        raise ValidationException(
            detail="Password must contain at least 1 symbol",
        )
