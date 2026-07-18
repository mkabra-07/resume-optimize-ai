from pydantic import BaseModel
from typing import List, Dict, Optional
from schemas.resume import ResumeContent
from schemas.ats import MissingSkills

class WeakBullet(BaseModel):
    section: str
    original: str
    reason: str

class GapAnalysisResponse(BaseModel):
    missing_keywords: List[str]
    missing_skills: MissingSkills
    weak_bullets: List[WeakBullet]
    suggested_improvements: List[str]
    ats_score_current: float
    ats_score_potential: float
    jd_similarity_percentage: float

class OptimizationResponse(BaseModel):
    version_id: int
    version_name: str
    original_resume_id: int
    optimized_content: ResumeContent
    ats_score_before: float
    ats_score_after: float
    changes_report: str
    download_docx_url: str
    download_pdf_url: str
