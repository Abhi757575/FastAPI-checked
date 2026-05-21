from src.db.main import get_session
from src import app
from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest
from auth.dependencies import Role_checker,AccessTokenBearer, RefreshTokenBearer

mock_session = Mock()
mock_user_service = Mock()
mock_book_Service = Mock()

def get_mock_session():
    yield mock_session

access_token_bearer = AccessTokenBearer()
role_checker = Role_checker()
refresh_token_bearer = RefreshTokenBearer(['admin'])


app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()

@pytest.fixture()
def fake_session():
    return mock_session

@pytest.fixture()
def fake_user_Service():
    return mock_user_service

@pytest.fixture()
def fake_book_Service():
    return mock_book_Service

@pytest.fixture()
def test_client():
    return TestClient(app)

