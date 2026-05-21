



from src.test.conftest import fake_session
from src.auth.schemas import UserCreateModel

auth_prefix = f"api/v1/auth"
sign_up_data = {
            "username" : "jod35",
            "email" : "jodestrevin@gmail.com",
            "first_name" : "jonathan",
            "last_name" : "ssali",
            "password": "test123",        
        }

def test_user_creation(fakesession, fake_user_service, test_client):

    response = test_client.post(
        url=f"{auth_prefix}/signup",
        json=sign_up_data,
    )

    user_data = UserCreateModel(**sign_up_data)

    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(sign_up_data['email'], fake_session)
    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(user_data, fake_session)
