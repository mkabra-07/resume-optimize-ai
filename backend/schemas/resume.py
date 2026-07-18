from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None

class ExperienceEntry(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    bullets: List[str]

class ProjectEntry(BaseModel):
    name: str
    description: str
    technologies: List[str]
    bullets: List[str]
    url: Optional[str] = None

class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None

class CertificationEntry(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None

class ResumeContent(BaseModel):
    contact: ContactInfo
    summary: Optional[str] = None
    skills: List[str]
    experience: List[ExperienceEntry]
    projects: List[ProjectEntry]
    education: List[EducationEntry]
    certifications: List[CertificationEntry]

class ResumeResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    is_original: bool
    content: ResumeContent
    created_at: datetime
