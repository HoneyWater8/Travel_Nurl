import pytest
from fastapi.testclient import TestClient
from app.main import app  # FastAPI 애플리케이션을 가져옵니다.
from app.schemas.user import UserCreate
import logging

logging.basicConfig(level=logging.DEBUG)
client = TestClient(app)


@pytest.fixture
def setup_database():
    # 테스트를 위한 데이터베이스 초기화 코드
    yield
    # 테스트 후 데이터베이스 정리 코드


def test_register_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "thumbnail_image_url": "file:///path/to/thumbnail.jpg",
        "profile_image_url": "file:///path/to/profile.jpg",
    }

    # 첫 번째 등록
    response = client.post("/register", json=user_data)
    logging.debug("First response: %s", response.json())
    logging.debug("Status code: %d", response.status_code)

    response = client.post("/register", json=user_data)
    logging.debug("Second response: %s", response.json())
    logging.debug("Status code: %d", response.status_code)
