import docx
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
        text_content = "\n".join(full_text)
        
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
