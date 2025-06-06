from pydantic import BaseModel
from typing import Optional


class APIRequest(BaseModel):
    text: str
    topic: Optional[str] = None
