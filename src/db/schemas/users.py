from src.db import sqlalchemy_table_to_pydantic
from src.db.models import User, Auth


register_Request = sqlalchemy_table_to_pydantic(
    model=User,
    name="UserRequest",
    exclude=[
        "id",
        "is_active",
    ],
    rename={
        "hashed_password": "password",
    },
    extra=[
        Auth.hashed_password,
    ],
)

user_Response = sqlalchemy_table_to_pydantic(
    model=User,
    name="UserResponse",
)
