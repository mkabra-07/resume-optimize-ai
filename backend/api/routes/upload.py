from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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

    from sqlalchemy import select
    # Check if duplicate exists
    query = select(Resume).where(Resume.file_hash == file_hash)
    result = await db.execute(query)
    existing_resume = result.scalars().first()
    if existing_resume:
        logger.info(f"Resume with hash {file_hash} already exists (ID: {existing_resume.id}). Returning existing record.")
        try:
            content_obj = ResumeContent.model_validate_json(existing_resume.content_json)
            return ResumeResponse(
                id=existing_resume.id,
                filename=existing_resume.filename,
                original_filename=existing_resume.original_filename,
                is_original=existing_resume.is_original,
                content=content_obj,
                created_at=existing_resume.created_at
            )
        except Exception as e:
            logger.error(f"Failed to validate existing resume JSON content: {e}. Re-parsing.")

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
        if os.path.exists(file_path):
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
