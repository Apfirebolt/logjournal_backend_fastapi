import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app
from config.db import Base
import config.db as sync_db
import auth.models
import journal.models
from auth.hashing import get_password_hash

# PostgreSQL Test Database URL (adjust credentials/dbname if needed)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:pass123@localhost:5432/logjournal_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override sync DB session factory
sync_db.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Fresh setup for the test session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed default test user ('ash@gmail.com') so login fixtures work instantly
    db = TestingSessionLocal()
    try:
        existing = db.query(auth.models.User).filter_by(email="ash@gmail.com").first()
        if not existing:
            # Note: auth.models.User.__init__ automatically hashes the password string
            test_user = auth.models.User(
                username="ash",
                email="ash@gmail.com",
                role="user",
                password="pass123"
            )
            db.add(test_user)
            db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c