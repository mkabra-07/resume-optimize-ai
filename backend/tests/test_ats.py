import pytest

def test_ats_scorer():
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

@pytest.mark.asyncio
async def test_ats_score_endpoint(test_client):
    import pytest
    from database import engine
    from models.resume import Resume
    from schemas.resume import ResumeContent, ContactInfo
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    resume_content = ResumeContent(
        contact=ContactInfo(name="John Doe"),
        summary="A software engineer",
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        db_resume = Resume(
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_hash="dummyhash",
            is_original=True,
            content_json=resume_content.model_dump_json()
        )
        session.add(db_resume)
        await session.commit()
        await session.refresh(db_resume)
        resume_id = db_resume.id

    response = test_client.post(
        "/api/v1/ats-score",
        json={"resume_id": resume_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert data["overall"] > 0
