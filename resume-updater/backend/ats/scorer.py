from schemas.ats import ATSScoreResponse, MissingSkills
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
