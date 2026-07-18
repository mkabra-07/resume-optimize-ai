import openai
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
                {"role": "user", "content": f"Resume: {resume.model_dump_json()}\n\nJD: {jd.model_dump_json()}"}
            ],
            response_format=GapAnalysisResponse
        )
        
        result = response.choices[0].message.parsed
        result.ats_score_current = current_score.overall
        return result

    async def optimize(self, resume: ResumeContent, jd: JobDescriptionContent, resume_id: int, instructions: str = None) -> OptimizationResponse:
        current_score = self.scorer.score(resume, jd)
        
        user_prompt = f"Resume: {resume.model_dump_json()}\n\nJD: {jd.model_dump_json()}"
        if instructions:
            user_prompt += f"\n\nUser Instructions: {instructions}"
            
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
