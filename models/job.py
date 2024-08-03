from typing import List, Optional
from pydantic import BaseModel

class Job(BaseModel):
    job_title: str
    company_name: str
    company_logo_url: Optional[str]
    location: str
    duration: Optional[str]
    stipend: Optional[str]
    status_info: Optional[str]
    job_type: Optional[str]

class PaginatedResponse(BaseModel):
    jobs: List[Job]
    total: int
    page: int
    size: int