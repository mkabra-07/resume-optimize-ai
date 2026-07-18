from fastapi import APIRouter, HTTPException, Depends
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
