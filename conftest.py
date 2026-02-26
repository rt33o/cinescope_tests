from faker import Faker
import pytest
import requests

import constants
from constants import BASE_URL, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from tests.api.api_manager import ApiManager

faker = Faker()



@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def test_movie():
    """
    Генерация случайного фильма для тестов.
    """
    random_movie = DataGenerator.generate_random_movie()

    return random_movie

@pytest.fixture(scope="function")
def updated_test_movie_data():
    """
    Генерация случайного фильма для тестов.
    """
    random_movie = DataGenerator.patch_random_movie()

    return random_movie


@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)

@pytest.fixture(scope="session")
def authorized_api_manager(api_manager):
    user_creds = constants.user_creds
    api_manager.auth_api.authenticate(user_creds)
    return api_manager



@pytest.fixture(scope="function")
def movie_factory(authorized_api_manager):
    """
    Фабрика: создаёт фильм и отдаёт его наружу.
    После теста удаляет все созданные фильмы.
    """
    created_movie_ids = []

    def _create(expected_status=201):
        test_movie = DataGenerator.generate_random_movie()
        response = authorized_api_manager.movies_api.create_movie(test_movie=test_movie, expected_status=expected_status, need_logging=False)
        data = response.json()

        get_movie_id = data.get('id')
        if get_movie_id:
            created_movie_ids.append(get_movie_id)
        return data

    return _create