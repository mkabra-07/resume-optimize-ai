"""
Keyword Matcher — compares resume skills/experience against JD requirements.

Uses fuzzy matching (difflib.SequenceMatcher) to handle variations like
"React.js" vs "React", "Kubernetes" vs "K8s", etc.

Returns:
  - keyword_score: 0–100 based on required skill coverage
  - MissingSkills breakdown: critical / important / optional
"""

import difflib
import re
from schemas.resume import ResumeContent
from schemas.job_description import JobDescriptionContent
from schemas.ats import MissingSkills

# Fuzzy match threshold: 0.0–1.0 (0.75 = lenient, 0.90 = strict)
MATCH_THRESHOLD = 0.78


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, expand common abbreviations."""
    text = text.lower().strip()
    text = re.sub(r"[.\-/\\+]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _fuzzy_match(skill: str, resume_tokens: set[str]) -> bool:
    """Return True if the skill fuzzy-matches any token in the resume pool."""
    norm_skill = _normalize(skill)
    for token in resume_tokens:
        ratio = difflib.SequenceMatcher(None, norm_skill, token).ratio()
        if ratio >= MATCH_THRESHOLD:
            return True
    return False


def _build_resume_token_pool(resume: ResumeContent) -> set[str]:
    """Collect all text tokens from the resume that might represent skills."""
    tokens: set[str] = set()

    # Direct skills list
    for s in resume.skills:
        tokens.add(_normalize(s))

    # Experience titles and bullet keywords
    for exp in resume.experience:
        tokens.add(_normalize(exp.title))
        for bullet in exp.bullets:
            # Extract capitalised and hyphenated words as potential tech terms
            words = re.findall(r"[A-Za-z][A-Za-z0-9\-\.+#]+", bullet)
            for w in words:
                tokens.add(_normalize(w))

    # Project technologies
    for proj in resume.projects:
        for tech in proj.technologies:
            tokens.add(_normalize(tech))

    return tokens


class KeywordMatcher:
    """Matches JD keywords against resume content using fuzzy matching."""

    def match(self, resume: ResumeContent, jd: JobDescriptionContent) -> tuple[float, MissingSkills]:
        """
        Compare JD required/preferred skills against the resume.

        Returns:
            (score: float 0–100, missing: MissingSkills)
        """
        resume_pool = _build_resume_token_pool(resume)

        required = jd.required_skills or []
        preferred = jd.preferred_skills or []

        # Critical = required skills not found
        critical_missing = [
            skill for skill in required if not _fuzzy_match(skill, resume_pool)
        ]
        # Important = preferred skills not found
        important_missing = [
            skill for skill in preferred if not _fuzzy_match(skill, resume_pool)
        ]

        # Score is based only on required skill coverage
        if not required:
            # No JD required skills specified — score based on preferred coverage
            if not preferred:
                score = 85.0  # Baseline when no JD skills available
            else:
                pct = (len(preferred) - len(important_missing)) / len(preferred)
                score = 50.0 + pct * 40.0  # 50–90 range
        else:
            coverage = (len(required) - len(critical_missing)) / len(required)
            score = coverage * 100.0

        missing = MissingSkills(
            critical=critical_missing,
            important=important_missing,
            optional=[],  # Could be extended with industry term analysis
        )
        return round(score, 1), missing

    def match_experience(self, resume: ResumeContent, jd: JobDescriptionContent) -> float:
        """
        Estimate experience match score (0–100).

        Heuristics:
          - Extracts years from JD requirement string
          - Estimates resume years from date ranges
          - Matches seniority level keywords
        """
        score = 80.0  # Default: assume reasonable match

        # --- Years check ---
        years_req_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", jd.years_of_experience or "", re.I)
        required_years: int | None = int(years_req_match.group(1)) if years_req_match else None

        if required_years:
            # Count experience entries as proxy (rough heuristic)
            num_jobs = len(resume.experience)
            if num_jobs == 0:
                score -= 30
            elif num_jobs == 1 and required_years >= 5:
                score -= 15
            elif num_jobs >= 3 and required_years <= 3:
                score = min(score + 10, 100)

        # --- Seniority check ---
        seniority = (jd.seniority_level or "").lower()
        if seniority:
            all_titles = " ".join(exp.title.lower() for exp in resume.experience)
            if "senior" in seniority or "lead" in seniority or "principal" in seniority:
                if not any(kw in all_titles for kw in ["senior", "lead", "principal", "staff", "architect"]):
                    score -= 15
            elif "junior" in seniority or "entry" in seniority:
                score = min(score + 5, 100)  # Junior JDs are easier to match

        return round(max(0.0, min(100.0, score)), 1)

    def get_important_missing(self, resume: ResumeContent, jd: JobDescriptionContent) -> list[str]:
        """Return just the list of important missing skills (for gap analysis)."""
        _, missing = self.match(resume, jd)
        return missing.important
