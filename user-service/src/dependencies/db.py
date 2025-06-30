from db import get_async_session
from fastapi import Depends

db_dependency = Depends(get_async_session)
