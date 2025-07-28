from fastapi import Depends
from user_service.db import get_async_session

db_dependency = Depends(get_async_session)
