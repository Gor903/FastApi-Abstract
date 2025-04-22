from fastapi import Depends
from src.db import get_async_session

async_session = Depends(get_async_session)
