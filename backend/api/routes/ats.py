from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from database import get_db
from models.resume import Resume
from models.job_description import JobDescription
from schemas.ats import ATSScoreResponse, ATSScoreRequest
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from ats.scorer import ATSScorer

router = APIRouter(tags=["ATS"])

@router.post("/ats-score", response_model=ATSScoreResponse)
async def get_ats_score(request: ATSScoreRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).filter(Resume.id == request.resume_id))
    resume_db = result.scalar_one_or_none()
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    resume_content = ResumeContent.model_validate_json(resume_db.content_json)
    
    jd_content = None
    if request.job_description_id:
        jd_result = await db.execute(select(JobDescription).filter(JobDescription.id == request.job_description_id))
        jd_db = jd_result.scalar_one_or_none()
        if not jd_db:
            raise HTTPException(status_code=404, detail="Job description not found")
        jd_content = JobDescriptionContent.model_validate_json(jd_db.parsed_json)
        
    scorer = ATSScorer()
    return scorer.score(resume_content, jd_content)
