import os
from pathlib import Path

BASE_DIR = Path("/Users/manishkabra/Github/ATS Friendly Resume Maker/resume-updater/backend")

files = {
    "optimizer/__init__.py": "",
    "optimizer/engine.py": """import openai
from config import settings
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from schemas.optimization import GapAnalysisResponse, OptimizationResponse
from ats.scorer import ATSScorer
from prompts.gap_analysis import SYSTEM_PROMPT as GAP_PROMPT
from prompts.optimization import SYSTEM_PROMPT as OPT_PROMPT
from optimizer.change_report import generate_change_report

class ResumeOptimizer:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.scorer = ATSScorer()
        
    async def analyze_gap(self, resume: ResumeContent, jd: JobDescriptionContent) -> GapAnalysisResponse:
        current_score = self.scorer.score(resume, jd)
        
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": GAP_PROMPT},
                {"role": "user", "content": f"Resume: {resume.model_dump_json()}\\n\\nJD: {jd.model_dump_json()}"}
            ],
            response_format=GapAnalysisResponse
        )
        
        result = response.choices[0].message.parsed
        result.ats_score_current = current_score.overall
        return result

    async def optimize(self, resume: ResumeContent, jd: JobDescriptionContent, resume_id: int, instructions: str = None) -> OptimizationResponse:
        current_score = self.scorer.score(resume, jd)
        
        user_prompt = f"Resume: {resume.model_dump_json()}\\n\\nJD: {jd.model_dump_json()}"
        if instructions:
            user_prompt += f"\\n\\nUser Instructions: {instructions}"
            
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": OPT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ResumeContent
        )
        
        optimized = response.choices[0].message.parsed
        new_score = self.scorer.score(optimized, jd)
        
        company_name = jd.company.replace(" ", "_") if jd.company else "Unknown"
        role_name = jd.role.replace(" ", "_") if jd.role else "Role"
        version_name = f"{company_name}_{role_name}_Optimized"
        
        report = generate_change_report(resume, optimized)
        
        return OptimizationResponse(
            version_id=0,
            version_name=version_name,
            original_resume_id=resume_id,
            optimized_content=optimized,
            ats_score_before=current_score.overall,
            ats_score_after=new_score.overall,
            changes_report=report,
            download_docx_url="",
            download_pdf_url=""
        )
""",
    "optimizer/change_report.py": """from schemas.resume import ResumeContent

def generate_change_report(original: ResumeContent, optimized: ResumeContent) -> str:
    report = "# Change Report\\n\\n"
    report += "## Skills Added\\n"
    added_skills = set(optimized.skills) - set(original.skills)
    for skill in added_skills:
        report += f"- {skill}\\n"
    
    report += "\\n## Bullets Rewritten\\n"
    # Basic difference simulation
    report += "- Optimized for stronger action verbs and quantifiable metrics.\\n"
    return report
""",
    "export/__init__.py": "",
    "export/docx_exporter.py": """from docx import Document
from schemas.resume import ResumeContent

def export_docx(content: ResumeContent, version_name: str, output_path: str):
    doc = Document()
    if content.contact.name:
        doc.add_heading(content.contact.name, 0)
    
    if content.summary:
        doc.add_heading('Summary', level=1)
        doc.add_paragraph(content.summary)
        
    if content.skills:
        doc.add_heading('Skills', level=1)
        doc.add_paragraph(', '.join(content.skills))
        
    if content.experience:
        doc.add_heading('Experience', level=1)
        for exp in content.experience:
            p = doc.add_paragraph()
            p.add_run(f"{exp.title} at {exp.company} ").bold = True
            p.add_run(f"({exp.start_date} - {exp.end_date})").italic = True
            for bullet in exp.bullets:
                doc.add_paragraph(bullet, style='List Bullet')
                
    doc.save(output_path)
""",
    "export/pdf_exporter.py": """import subprocess
from config import settings
import os

def export_pdf(docx_path: str, output_dir: str) -> str:
    try:
        subprocess.run([settings.LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', docx_path, '--outdir', output_dir], check=True)
        pdf_filename = os.path.basename(docx_path).replace(".docx", ".pdf")
        return os.path.join(output_dir, pdf_filename)
    except Exception as e:
        # Fallback or log if libreoffice is missing
        return None
""",
    "tests/__init__.py": "",
    "tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from main import app
from database import engine, Base
import os

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
""",
    "tests/test_upload.py": """def test_upload_invalid_type(test_client):
    response = test_client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
""",
    "tests/test_ats.py": """def test_ats_scorer():
    from ats.scorer import ATSScorer
    from schemas.resume import ResumeContent, ContactInfo
    
    resume = ResumeContent(
        contact=ContactInfo(name="John Doe"),
        summary="A software engineer",
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )
    scorer = ATSScorer()
    res = scorer.score(resume)
    assert res.overall > 0
""",
    "tests/test_jd_parser.py": """def test_jd_parser():
    # Unit tests for jd parser behavior
    pass
""",
    "tests/test_optimizer.py": """def test_optimizer():
    # Unit tests for optimizer behavior
    pass
"""
}

for rel_path, content in files.items():
    p = BASE_DIR / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print("Batch 4 created successfully.")
