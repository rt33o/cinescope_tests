from http.client import responses

from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, BASE_URL
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL)

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        """

        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds: dict):

        response =  self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=user_creds
        )


        data = response.json()
        token = data.get("accessToken")
        if not token:
            raise KeyError("accessToken is missing")

        self._update_session_headers(Authorization=f"Bearer {token}")

        return response

