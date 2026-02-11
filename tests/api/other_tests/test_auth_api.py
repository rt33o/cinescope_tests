
import pytest
from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    def test_register_user(self, requester, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, requester, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=201
        )
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

