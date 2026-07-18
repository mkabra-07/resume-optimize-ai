import pytest
import os

# Override database URL for tests to avoid wiping development database
from config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///test_resume_updater.db"

from fastapi.testclient import TestClient
from main import app
from database import engine, Base

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db(request):
    def remove_file():
        try:
            if os.path.exists("test_resume_updater.db"):
                os.remove("test_resume_updater.db")
        except Exception:
            pass
    request.addfinalizer(remove_file)

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
