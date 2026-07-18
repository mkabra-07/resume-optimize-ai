from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.resume import Resume, ResumeVersion
from models.job_description import JobDescription
from schemas.optimization import GapAnalysisResponse, OptimizationResponse
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from optimizer.engine import ResumeOptimizer
from ats.scorer import ATSScorer
from export.docx_exporter import export_docx
from export.pdf_exporter import export_pdf
from config import settings
import json
import os

router = APIRouter(tags=["Optimization"])

class AnalyzeGapRequest(BaseModel):
    resume_id: int
    job_description_id: int

class OptimizeRequest(BaseModel):
    resume_id: int
    job_description_id: int
    instructions: Optional[str] = None

@router.post("/analyze-gap", response_model=GapAnalysisResponse)
async def analyze_gap(request: AnalyzeGapRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Resume).filter(Resume.id == request.resume_id))
    resume_db = res.scalar_one_or_none()
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    jd_res = await db.execute(select(JobDescription).filter(JobDescription.id == request.job_description_id))
    jd_db = jd_res.scalar_one_or_none()
    if not jd_db:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    resume_content = ResumeContent.model_validate_json(resume_db.content_json)
    jd_content = JobDescriptionContent.model_validate_json(jd_db.parsed_json)
    
    optimizer = ResumeOptimizer()
    return await optimizer.analyze_gap(resume_content, jd_content)

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_resume(request: OptimizeRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Resume).filter(Resume.id == request.resume_id))
    resume_db = res.scalar_one_or_none()
    if not resume_db or not resume_db.is_original:
        raise HTTPException(status_code=404, detail="Original resume not found")
        
    jd_res = await db.execute(select(JobDescription).filter(JobDescription.id == request.job_description_id))
    jd_db = jd_res.scalar_one_or_none()
    if not jd_db:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    resume_content = ResumeContent.model_validate_json(resume_db.content_json)
    jd_content = JobDescriptionContent.model_validate_json(jd_db.parsed_json)
    
    optimizer = ResumeOptimizer()
    opt_resp = await optimizer.optimize(resume_content, jd_content, request.resume_id, request.instructions)
    
    # Generate DOCX
    docx_path = os.path.join(settings.EXPORT_DIR, f"{opt_resp.version_name}.docx")
    export_docx(opt_resp.optimized_content, opt_resp.version_name, docx_path)
    
    # Generate PDF
    pdf_path = export_pdf(docx_path, settings.EXPORT_DIR)
    
    # Save version to DB
    new_version = ResumeVersion(
        original_resume_id=request.resume_id,
        filename=f"{opt_resp.version_name}.docx",
        file_path_docx=docx_path,
        file_path_pdf=pdf_path,
        job_description_id=request.job_description_id,
        ats_score_before=opt_resp.ats_score_before,
        ats_score_after=opt_resp.ats_score_after,
        changes_json=opt_resp.changes_report,
        optimized_content_json=opt_resp.optimized_content.model_dump_json(),
        version_name=opt_resp.version_name
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    
    opt_resp.version_id = new_version.id
    opt_resp.download_docx_url = f"/api/v1/download/docx/{new_version.id}"
    opt_resp.download_pdf_url = f"/api/v1/download/pdf/{new_version.id}"
    
    return opt_resp

@router.get("/resume/{id}")
async def get_resume(id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Resume).filter(Resume.id == id))
    resume = res.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    content = ResumeContent.model_validate_json(resume.content_json)
    return {
        "id": resume.id,
        "filename": resume.filename,
        "original_filename": resume.original_filename,
        "is_original": resume.is_original,
        "content": content,
        "created_at": resume.created_at
    }

@router.get("/changes/{version_id}")
async def get_changes(version_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).filter(ResumeVersion.id == version_id))
    version = res.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"changes_report": version.changes_json}

@router.get("/library/stats")
async def get_library_stats(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    versions_count_res = await db.execute(select(func.count(ResumeVersion.id)))
    total_versions = versions_count_res.scalar() or 0
    
    avg_score_res = await db.execute(select(func.avg(ResumeVersion.ats_score_after)))
    avg_ats_score = avg_score_res.scalar() or 0.0
    avg_ats_score = round(float(avg_ats_score), 1) if avg_ats_score else 0.0
    
    base_resumes_res = await db.execute(select(func.count(Resume.id)).filter(Resume.is_original == True))
    base_resumes = base_resumes_res.scalar() or 0
    
    return {
        "total_versions": total_versions,
        "avg_ats_score": avg_ats_score,
        "base_resumes": base_resumes
    }

@router.get("/library/versions")
async def get_library_versions(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).order_by(ResumeVersion.created_at.desc()))
    versions = res.scalars().all()
    
    return [
        {
            "id": v.id,
            "name": v.version_name or v.filename,
            "score": v.ats_score_after,
            "date": v.created_at.strftime("%Y-%m-%d") if v.created_at else None
        }
        for v in versions
    ]
