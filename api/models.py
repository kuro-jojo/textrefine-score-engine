from pydantic import BaseModel
from typing import Optional, Literal

# Define valid audience types
AudienceType = Literal[
    'children',
    'teenagers',
    'young_adults',
    'general',
    'business',
    'professional',
    'academic'
]

class APIRequest(BaseModel):
    text: str
    topic: Optional[str] = None
    audience: Optional[AudienceType] = None
