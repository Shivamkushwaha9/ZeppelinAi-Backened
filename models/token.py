from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None