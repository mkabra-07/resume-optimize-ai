import openai
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
