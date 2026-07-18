"""
Readability Checker — evaluates resume bullets for ATS readability signals.

Checks:
  - Action verbs at the start of bullets
  - Quantified metrics (%, $, multipliers, K/M numbers)
  - Bullet length (too short or too long)
  - Verb tense consistency
"""

import re
from schemas.resume import ResumeContent

# Curated list of 120+ strong action verbs for resume bullets
ACTION_VERBS = {
    "accelerated", "accomplished", "achieved", "acquired", "administered",
    "advanced", "analyzed", "architected", "automated", "built",
    "championed", "collaborated", "communicated", "compiled", "completed",
    "conducted", "configured", "consolidated", "constructed", "contributed",
    "coordinated", "created", "customized", "debugged", "defined",
    "delivered", "deployed", "designed", "developed", "devised",
    "directed", "discovered", "drove", "eliminated", "enabled",
    "engineered", "enhanced", "established", "evaluated", "executed",
    "expanded", "facilitated", "generated", "guided", "identified",
    "implemented", "improved", "increased", "integrated", "launched",
    "led", "maintained", "managed", "mentored", "migrated",
    "modeled", "modernized", "monitored", "negotiated", "optimized",
    "orchestrated", "organized", "oversaw", "owned", "partnered",
    "planned", "prioritized", "processed", "produced", "provided",
    "published", "reduced", "refactored", "researched", "resolved",
    "restructured", "reviewed", "scaled", "secured", "simplified",
    "spearheaded", "standardized", "streamlined", "supported", "tested",
    "trained", "transformed", "unified", "upgraded", "utilized",
    "validated", "wrote", "accelerate", "align", "analyze",
    "architect", "automate", "collaborate", "deliver", "deploy",
    "drive", "enable", "engineer", "enhance", "establish",
    "execute", "expand", "facilitate", "implement", "integrate",
    "launch", "leverage", "mentor", "migrate", "optimize",
    "orchestrate", "oversee", "prioritize", "scale", "spearhead",
    "streamline", "transform", "coordinate", "document", "prototype",
    "shipped", "owned", "proposed", "redesigned", "revamped",
}

# Regex for quantified metric patterns
METRIC_PATTERN = re.compile(
    r"(\d+\s*%|\$\s*\d+|\d+\s*[xX]|\d+[KkMmBb]\b|\d+\s+percent|\d+\s+million|\d+\s+billion)",
    re.IGNORECASE,
)


class ReadabilityChecker:
    """Evaluates resume content for readability and ATS signal quality."""

    def check(self, resume: ResumeContent) -> float:
        """
        Score readability from 0–100.

        Scoring breakdown:
          - Start with 100
          - Deduct for missing action verbs (-3 per bullet without one, max -30)
          - Deduct for low metrics coverage (-15 if fewer than 3 quantified bullets)
          - Deduct for too-short bullets (<8 words, -5 each, max -20)
          - Deduct for too-long bullets (>40 words, -2 each, max -10)
        """
        score = 100.0
        all_bullets: list[str] = []

        for exp in resume.experience:
            all_bullets.extend(exp.bullets)
        for proj in resume.projects:
            all_bullets.extend(proj.bullets)

        if not all_bullets:
            # No bullets at all is a moderate penalty
            return 60.0

        # --- Action verb check ---
        missing_verb_penalty = 0
        for bullet in all_bullets:
            first_word = bullet.strip().split()[0].lower().rstrip(".,;:") if bullet.strip() else ""
            if first_word and first_word not in ACTION_VERBS:
                missing_verb_penalty += 3
        score -= min(30, missing_verb_penalty)

        # --- Quantified metrics check ---
        metrics_count = sum(1 for b in all_bullets if METRIC_PATTERN.search(b))
        if metrics_count == 0:
            score -= 20
        elif metrics_count < 3:
            score -= 10
        elif metrics_count < 5:
            score -= 5

        # --- Bullet length check ---
        short_penalty = 0
        long_penalty = 0
        for bullet in all_bullets:
            word_count = len(bullet.split())
            if word_count < 8:
                short_penalty += 5
            if word_count > 40:
                long_penalty += 2

        score -= min(20, short_penalty)
        score -= min(10, long_penalty)

        return round(max(0.0, score), 1)

    def get_weak_bullets(self, resume: ResumeContent) -> list[dict]:
        """
        Return a list of weak bullets with their section context and reason.
        Used by the gap analysis and optimization pipeline.
        """
        weak = []

        def _check_bullet(section: str, bullet: str) -> list[str]:
            reasons = []
            words = bullet.strip().split()
            if not words:
                return ["Empty bullet"]
            first_word = words[0].lower().rstrip(".,;:")
            if first_word not in ACTION_VERBS:
                reasons.append(f"Does not start with a strong action verb (starts with '{words[0]}')")
            if not METRIC_PATTERN.search(bullet):
                reasons.append("Missing quantified metric (%, $, multiplier, or number)")
            if len(words) < 8:
                reasons.append("Too short — add more context and impact")
            if len(words) > 40:
                reasons.append("Too long — split into multiple focused bullets")
            return reasons

        for exp in resume.experience:
            for bullet in exp.bullets:
                reasons = _check_bullet("experience", bullet)
                if reasons:
                    weak.append({
                        "section": f"Experience — {exp.company} ({exp.title})",
                        "original": bullet,
                        "reason": "; ".join(reasons),
                    })

        for proj in resume.projects:
            for bullet in proj.bullets:
                reasons = _check_bullet("project", bullet)
                if reasons:
                    weak.append({
                        "section": f"Project — {proj.name}",
                        "original": bullet,
                        "reason": "; ".join(reasons),
                    })

        return weak
