from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobDescriptionContent(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    years_of_experience: Optional[str] = None
    qualifications: List[str]
    industry: Optional[str] = None
    seniority_level: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    id: int
    source_type: str
    source_url: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    content: JobDescriptionContent
    created_at: datetime
