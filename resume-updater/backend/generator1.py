import os
from pathlib import Path

BASE_DIR = Path("/Users/manishkabra/Github/ATS Friendly Resume Maker/resume-updater/backend")

files = {
    "requirements.txt": """fastapi==0.111.0
uvicorn[standard]==0.29.0
python-multipart==0.0.9
pydantic==2.7.0
pydantic-settings==2.2.1
sqlalchemy==2.0.30
alembic==1.13.1
aiosqlite==0.20.0
openai==1.30.1
httpx==0.27.0
beautifulsoup4==4.12.3
lxml==5.2.2
python-docx==1.1.0
pdfplumber==0.11.0
pypdf==4.2.0
python-dotenv==1.0.1
loguru==0.7.2
tiktoken==0.7.0
pytest==8.2.0
pytest-asyncio==0.23.6
chardet==5.2.0
Markdownify==0.12.1""",

    "config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_updater.db"
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    LIBREOFFICE_PATH: str = "/usr/bin/libreoffice"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
""",

    "database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")
""",

    ".env.example": """OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./resume_updater.db
UPLOAD_DIR=./uploads
EXPORT_DIR=./exports
LIBREOFFICE_PATH=/usr/bin/libreoffice
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO""",

    "Dockerfile": """FROM python:3.11-slim

RUN apt-get update && apt-get install -y libreoffice --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads exports

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    "alembic.ini": """[alembic]
script_location = alembic
sqlalchemy.url = sqlite+aiosqlite:///./resume_updater.db

[post_write_hooks]
[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S""",

    "alembic/env.py": """import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from database import Base
from config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
""",

    "alembic/versions/.gitkeep": "",

    "models/__init__.py": """from .resume import Resume, ResumeVersion
from .job_description import JobDescription
""",

    "models/resume.py": """from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
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
""",

    "models/job_description.py": """from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String)
    source_url = Column(String, nullable=True)
    raw_text = Column(Text)
    parsed_json = Column(Text)
    company = Column(String, nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",

    "schemas/__init__.py": "",

    "schemas/resume.py": """from pydantic import BaseModel
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
""",

    "schemas/job_description.py": """from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobDescriptionContent(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    years_of_experience: Optional[str] = None
    qualifications: List[str]
    industry: Optional[str] = None
    seniority_level: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    id: int
    source_type: str
    source_url: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    content: JobDescriptionContent
    created_at: datetime
""",

    "schemas/ats.py": """from pydantic import BaseModel
from typing import List, Dict

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
""",

    "schemas/optimization.py": """from pydantic import BaseModel
from typing import List, Dict, Optional
from schemas.resume import ResumeContent
from schemas.ats import MissingSkills

class GapAnalysisResponse(BaseModel):
    missing_keywords: List[str]
    missing_skills: MissingSkills
    weak_bullets: List[Dict[str, str]]
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
""",
    
    "main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from config import settings
from database import init_db
from api.routes import upload, ats, job_description, optimization, export
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Resume Updater & ATS Optimizer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1")
app.include_router(ats.router, prefix="/api/v1")
app.include_router(job_description.router, prefix="/api/v1")
app.include_router(optimization.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "healthy"}
"""
}

for rel_path, content in files.items():
    p = BASE_DIR / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print("Batch 1 created successfully.")
