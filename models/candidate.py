from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class CandidateModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')  
    email: EmailStr
    password: str = Field(..., min_length=6)
    photo: Optional[str] = None  # ObjectId of the profile photo in GridFS

class CandidateLoginModel(BaseModel):
    username: str
    password: str

class ChangePasswordModel(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class CandidateUpdateModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]