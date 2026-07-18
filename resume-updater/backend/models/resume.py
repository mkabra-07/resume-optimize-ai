from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    file_hash = Column(String, unique=True, index=True)
    is_original = Column(Boolean, default=True)
    content_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    original_resume_id = Column(Integer, ForeignKey("resumes.id"))
    filename = Column(String)
    file_path_docx = Column(String)
    file_path_pdf = Column(String, nullable=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    ats_score_before = Column(Float, nullable=True)
    ats_score_after = Column(Float, nullable=True)
    changes_json = Column(Text)
    optimized_content_json = Column(Text)
    version_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
