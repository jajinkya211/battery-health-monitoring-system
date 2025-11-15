"""API endpoint tests"""
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.database import get_db_session, init_db
from backend.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_battery_pack():
    """Test battery pack creation"""
    response = client.post(
        "/battery_packs",
        json={
            "model": "Test Pack",
            "chemistry": "NMC",
            "capacity_ah": 50.0,
            "manufacture_date": "2024-01-01"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["model"] == "Test Pack"
    assert data["chemistry"] == "NMC"


def test_get_battery_packs():
    """Test getting battery packs"""
    response = client.get("/battery_packs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user():
    """Test user creation"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "role": "engineer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"


def test_create_health_threshold():
    """Test health threshold creation"""
    response = client.post(
        "/health_thresholds",
        json={
            "metric_type": "soh",
            "min_value": 80.0,
            "max_value": None,
            "severity": "warning"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metric_type"] == "soh"