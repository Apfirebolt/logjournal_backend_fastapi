import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app  # Assuming your main FastAPI app instance is here
from config.db import Base
from auth.jwt import get_current_user
from auth import schema as auth_schema

# Use SQLite in-memory for fast isolated testing (or point to a test postgres DB)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database session maker used in sync db functions
import config.db as sync_db
sync_db.SessionLocal = TestingSessionLocal


@pytest.fixture(autouse=True)
import journal.models  # Ensure models are registered
import auth.models     # Ensure auth models are registered

def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Mock current user dependency so we can test endpoints easily
def override_get_current_user():
    return auth_schema.TokenData(id=1, email="alice@example.com")

app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c