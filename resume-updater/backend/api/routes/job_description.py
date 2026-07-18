from fastapi import APIRouter, HTTPException, Depends
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
