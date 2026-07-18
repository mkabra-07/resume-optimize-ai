import os
from pathlib import Path

BASE_DIR = Path("/Users/manishkabra/Github/ATS Friendly Resume Maker/resume-updater/backend")

files = {
    "resume_parser/__init__.py": "",
    "resume_parser/base.py": """from abc import ABC, abstractmethod
from schemas.resume import ResumeContent

class BaseResumeParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ResumeContent:
        pass
""",
    "resume_parser/docx_parser.py": """import docx
from resume_parser.base import BaseResumeParser
from schemas.resume import ResumeContent
import openai
from config import settings
from prompts.resume_extraction import SYSTEM_PROMPT
import json
from loguru import logger

class DocxParser(BaseResumeParser):
    def parse(self, file_path: str) -> ResumeContent:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        text_content = "\\n".join(full_text)
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text_content}
            ],
            response_format=ResumeContent
        )
        
        return response.choices[0].message.parsed
""",
    "resume_parser/pdf_parser.py": """import pdfplumber
from pypdf import PdfReader
from resume_parser.base import BaseResumeParser
from schemas.resume import ResumeContent
import openai
from config import settings
from prompts.resume_extraction import SYSTEM_PROMPT

class PdfParser(BaseResumeParser):
    def parse(self, file_path: str) -> ResumeContent:
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\\n"
        except Exception:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text_content += page.extract_text() + "\\n"
                
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text_content}
            ],
            response_format=ResumeContent
        )
        
        return response.choices[0].message.parsed
""",
    "ats/__init__.py": "",
    "ats/scorer.py": """from schemas.ats import ATSScoreResponse, MissingSkills
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from ats.keyword_matcher import KeywordMatcher
from ats.formatting_checker import FormattingChecker
from ats.readability import ReadabilityChecker

class ATSScorer:
    def __init__(self):
        self.keyword_matcher = KeywordMatcher()
        self.formatting_checker = FormattingChecker()
        self.readability_checker = ReadabilityChecker()

    def score(self, resume: ResumeContent, jd: JobDescriptionContent = None) -> ATSScoreResponse:
        missing_skills = MissingSkills(critical=[], important=[], optional=[])
        keyword_score = 100.0
        exp_score = 100.0
        if jd:
            keyword_score, missing_skills = self.keyword_matcher.match(resume, jd)
            exp_score = self.keyword_matcher.match_experience(resume, jd)
            
        formatting_issues = self.formatting_checker.check(resume)
        formatting_score = 100.0 - (len(formatting_issues) * 10)
        formatting_score = max(0, formatting_score)
        
        sections = {
            "summary": bool(resume.summary),
            "skills": bool(resume.skills),
            "experience": bool(resume.experience),
            "education": bool(resume.education)
        }
        completeness = sum(sections.values()) / len(sections) * 100
        
        readability = self.readability_checker.check(resume)
        
        overall = (
            keyword_score * 0.30 +
            exp_score * 0.25 +
            formatting_score * 0.20 +
            completeness * 0.15 +
            readability * 0.10
        )
        
        return ATSScoreResponse(
            overall=round(overall, 1),
            keyword_match=round(keyword_score, 1),
            experience_match=round(exp_score, 1),
            formatting=round(formatting_score, 1),
            section_completeness=round(completeness, 1),
            readability=round(readability, 1),
            missing_skills=missing_skills,
            formatting_issues=formatting_issues,
            recommendations=["Add more quantifiable metrics"] if readability < 80 else [],
            sections_present=sections
        )
""",
    "ats/keyword_matcher.py": """from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from schemas.ats import MissingSkills
import difflib

class KeywordMatcher:
    def match(self, resume: ResumeContent, jd: JobDescriptionContent):
        req_skills = set(jd.required_skills)
        res_skills = set(resume.skills)
        
        critical_missing = []
        for req in req_skills:
            if not any(difflib.SequenceMatcher(None, req.lower(), res.lower()).ratio() > 0.8 for res in res_skills):
                critical_missing.append(req)
                
        score = 100 if not req_skills else ((len(req_skills) - len(critical_missing)) / len(req_skills)) * 100
        return score, MissingSkills(critical=critical_missing, important=[], optional=jd.preferred_skills)

    def match_experience(self, resume: ResumeContent, jd: JobDescriptionContent):
        # Placeholder for simple experience matching
        return 80.0
""",
    "ats/formatting_checker.py": """from schemas.resume import ResumeContent
from schemas.ats import FormattingIssue

class FormattingChecker:
    def check(self, resume: ResumeContent):
        issues = []
        # Complex DOCX/PDF check would be implemented here, stubbed out for simplicity
        return issues
""",
    "ats/readability.py": """from schemas.resume import ResumeContent
import re

class ReadabilityChecker:
    def check(self, resume: ResumeContent):
        score = 100.0
        metrics_found = 0
        for exp in resume.experience:
            for bullet in exp.bullets:
                if re.search(r'\\d+%|\\$\\d+|\\d+x|\\d+K|\\d+M', bullet):
                    metrics_found += 1
                if len(bullet.split()) < 5:
                    score -= 5
                if len(bullet.split()) > 40:
                    score -= 2
        
        if metrics_found < 3:
            score -= 15
            
        return max(0, score)
""",
    "jd_parser/__init__.py": "",
    "jd_parser/text_parser.py": """import openai
from config import settings
from schemas.job_description import JobDescriptionContent
from prompts.jd_parsing import SYSTEM_PROMPT

async def parse_jd_text(text: str) -> JobDescriptionContent:
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    response = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        response_format=JobDescriptionContent
    )
    
    return response.choices[0].message.parsed
""",
    "jd_parser/url_scraper.py": """import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

async def scrape_jd_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        
    soup = BeautifulSoup(resp.text, 'lxml')
    # Strip unnecessary elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    markdown_text = markdownify(str(soup), heading_style="ATX")
    return markdown_text.strip()
"""
}

for rel_path, content in files.items():
    p = BASE_DIR / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print("Batch 3 created successfully.")
