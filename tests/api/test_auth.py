import pytest
import requests

from conftest import session
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT,  LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, user_creds, session):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": user_creds["email"],
            "password": user_creds["password"]
        }
        response = api_manager.auth_api.authenticate(login_data)
        response_data = response.json()

        token = response_data["accessToken"]

        # print(api_manager.session)


        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == user_creds["email"], "Email не совпадает"