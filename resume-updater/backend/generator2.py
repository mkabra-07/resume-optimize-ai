import os
from pathlib import Path

BASE_DIR = Path("/Users/manishkabra/Github/ATS Friendly Resume Maker/resume-updater/backend")

files = {
    "api/__init__.py": "",
    "api/routes/__init__.py": "",
    "api/routes/upload.py": """from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import hashlib
import uuid
import os
import json
from loguru import logger
from database import get_db
from models.resume import Resume
from schemas.resume import ResumeResponse, ResumeContent
from config import settings
from resume_parser.docx_parser import DocxParser
from resume_parser.pdf_parser import PdfParser

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # Validate file size
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

    # Validate file type
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    # Hash file for integrity
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Parse resume
    try:
        if ext == 'docx':
            parser = DocxParser()
        else:
            parser = PdfParser()
            
        content_obj = parser.parse(file_path)
        content_json = content_obj.model_dump_json()
    except Exception as e:
        logger.error(f"Failed to parse resume: {e}")
        os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to parse resume content")

    # Save to db
    db_resume = Resume(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_hash=file_hash,
        is_original=True,
        content_json=content_json
    )
    db.add(db_resume)
    await db.commit()
    await db.refresh(db_resume)

    return ResumeResponse(
        id=db_resume.id,
        filename=db_resume.filename,
        original_filename=db_resume.original_filename,
        is_original=db_resume.is_original,
        content=content_obj,
        created_at=db_resume.created_at
    )
""",

    "api/routes/ats.py": """from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from database import get_db
from models.resume import Resume
from models.job_description import JobDescription
from schemas.ats import ATSScoreResponse
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from ats.scorer import ATSScorer

router = APIRouter(tags=["ATS"])

@router.post("/ats-score", response_model=ATSScoreResponse)
async def get_ats_score(resume_id: int, job_description_id: int = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).filter(Resume.id == resume_id))
    resume_db = result.scalar_one_or_none()
    if not resume_db:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    resume_content = ResumeContent.model_validate_json(resume_db.content_json)
    
    jd_content = None
    if job_description_id:
        jd_result = await db.execute(select(JobDescription).filter(JobDescription.id == job_description_id))
        jd_db = jd_result.scalar_one_or_none()
        if not jd_db:
            raise HTTPException(status_code=404, detail="Job description not found")
        jd_content = JobDescriptionContent.model_validate_json(jd_db.parsed_json)
        
    scorer = ATSScorer()
    return scorer.score(resume_content, jd_content)
""",

    "api/routes/job_description.py": """from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database import get_db
from models.job_description import JobDescription
from schemas.job_description import JobDescriptionResponse, JobDescriptionContent
from jd_parser.text_parser import parse_jd_text
from jd_parser.url_scraper import scrape_jd_url
import json

router = APIRouter(tags=["Job Description"])

class JDRequest(BaseModel):
    source_type: str
    content: str

@router.post("/job-description", response_model=JobDescriptionResponse)
async def process_job_description(request: JDRequest, db: AsyncSession = Depends(get_db)):
    if request.source_type not in ["text", "url"]:
        raise HTTPException(status_code=400, detail="source_type must be 'text' or 'url'")
        
    try:
        if request.source_type == "url":
            raw_text = await scrape_jd_url(request.content)
            source_url = request.content
        else:
            raw_text = request.content
            source_url = None
            
        content_obj = await parse_jd_text(raw_text)
        
        db_jd = JobDescription(
            source_type=request.source_type,
            source_url=source_url,
            raw_text=raw_text,
            parsed_json=content_obj.model_dump_json(),
            company=content_obj.company,
            role=content_obj.role
        )
        db.add(db_jd)
        await db.commit()
        await db.refresh(db_jd)
        
        return JobDescriptionResponse(
            id=db_jd.id,
            source_type=db_jd.source_type,
            source_url=db_jd.source_url,
            company=db_jd.company,
            role=db_jd.role,
            content=content_obj,
            created_at=db_jd.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""",

    "api/routes/optimization.py": """from fastapi import APIRouter, HTTPException, Depends
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
""",

    "api/routes/export.py": """from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.resume import ResumeVersion
import os

router = APIRouter(tags=["Export"])

@router.get("/download/docx/{version_id}")
async def download_docx(version_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).filter(ResumeVersion.id == version_id))
    version = res.scalar_one_or_none()
    if not version or not os.path.exists(version.file_path_docx):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(version.file_path_docx, filename=version.filename)

@router.get("/download/pdf/{version_id}")
async def download_pdf(version_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).filter(ResumeVersion.id == version_id))
    version = res.scalar_one_or_none()
    if not version or not version.file_path_pdf or not os.path.exists(version.file_path_pdf):
        raise HTTPException(status_code=404, detail="File not found")
    pdf_filename = version.filename.replace(".docx", ".pdf")
    return FileResponse(version.file_path_pdf, filename=pdf_filename)

@router.get("/download/report/{version_id}")
async def download_report(version_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).filter(ResumeVersion.id == version_id))
    version = res.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report": version.changes_json}

@router.get("/download/json/{version_id}")
async def download_json(version_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResumeVersion).filter(ResumeVersion.id == version_id))
    version = res.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"content": version.optimized_content_json}
""",

    "prompts/__init__.py": "",

    "prompts/resume_extraction.py": """SYSTEM_PROMPT = \"\"\"You are an expert resume parser. Extract all information from the resume text into the structured format. Be thorough and accurate. Do not infer or invent information. Output strictly in the requested JSON structure.\"\"\"
""",

    "prompts/jd_parsing.py": """SYSTEM_PROMPT = \"\"\"You are an expert job description analyst. Extract all structured information from the job posting. Categorize skills as required vs preferred. Ensure the extracted content accurately represents the provided text without inventing any new details.\"\"\"
""",

    "prompts/gap_analysis.py": """SYSTEM_PROMPT = \"\"\"You are an ATS expert. Analyze the gap between the resume and job description. Identify missing keywords, weak bullets, and specific improvements needed. Be specific and actionable.\"\"\"
""",

    "prompts/optimization.py": """SYSTEM_PROMPT = \"\"\"You are an expert ATS resume optimizer. Rules:
1. NEVER fabricate companies, projects, achievements, numbers, or responsibilities.
2. If information to add does not exist in the original resume, do not add it.
3. You may: rewrite bullets with stronger action verbs, reorder skills, emphasize relevant technologies, improve the summary, optimize keyword placement.
4. Always preserve factual correctness.
5. Optimize for ATS while maintaining human readability.\"\"\"
"""
}

for rel_path, content in files.items():
    p = BASE_DIR / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print("Batch 2 created successfully.")
