import pdfplumber
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
                    text_content += page.extract_text() + "\n"
        except Exception:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
                
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
