import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure project root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # <-- Imports main.py from root level
from config.db import Base
import config.db as sync_db
from auth.jwt import get_current_user
from auth import schema as auth_schema

# Ensure all SQLAlchemy models are registered before tables are created
import auth.models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database session maker used in sync db functions
sync_db.SessionLocal = TestingSessionLocal


@pytest.fixture(autouse=True)
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