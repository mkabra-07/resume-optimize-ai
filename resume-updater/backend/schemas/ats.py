from pydantic import BaseModel
from typing import List, Dict, Optional

class ATSScoreRequest(BaseModel):
    resume_id: int
    job_description_id: Optional[int] = None


class MissingSkills(BaseModel):
    critical: List[str]
    important: List[str]
    optional: List[str]

class FormattingIssue(BaseModel):
    issue_type: str
    description: str
    severity: str

class ATSScoreResponse(BaseModel):
    overall: float
    keyword_match: float
    experience_match: float
    formatting: float
    section_completeness: float
    readability: float
    missing_skills: MissingSkills
    formatting_issues: List[FormattingIssue]
    recommendations: List[str]
    sections_present: Dict[str, bool]
