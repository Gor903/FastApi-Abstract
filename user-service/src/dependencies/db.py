from fastapi import Depends

from db import get_async_session

db_dependency = Depends(get_async_session)
