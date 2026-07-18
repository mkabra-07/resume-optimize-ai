from schemas.resume import ResumeContent

def generate_change_report(original: ResumeContent, optimized: ResumeContent) -> str:
    report = "# Change Report\n\n"
    report += "## Skills Added\n"
    added_skills = set(optimized.skills) - set(original.skills)
    for skill in added_skills:
        report += f"- {skill}\n"
    
    report += "\n## Bullets Rewritten\n"
    # Basic difference simulation
    report += "- Optimized for stronger action verbs and quantifiable metrics.\n"
    return report
