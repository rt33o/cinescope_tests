from faker import Faker
import pytest
import requests


from constants import constants
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from tests.api.api_manager import ApiManager
from resources.user_creds import SuperAdminCreds
from entities.user import User
from constants.roles import Roles
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
# from models.user import RegistrationUserModel

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
    Генерация частичного обновления фильма для тестов.
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
        endpoint=constants.REGISTER_ENDPOINT,
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
    return CustomRequester(session=session, base_url=constants.BASE_URL)

@pytest.fixture(scope="function")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="function")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)

@pytest.fixture(scope="function")
def authorized_api_manager(api_manager):
    """
    Фикстура для создания экземпляра ApiManager с правами админа.
    """
    user_creds = constants.user_creds
    api_manager.auth_api.authenticate(user_creds)
    return api_manager



@pytest.fixture(scope="function")
def movie_factory(authorized_api_manager):
    """
    Фабрика: создаёт фильм и отдаёт его наружу.
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

    yield _create

    for m_id in created_movie_ids:
        authorized_api_manager.movies_api.delete_movie(movie_id=m_id)


@pytest.fixture(scope="session")
def user_session():
    """
    Создает юзер-сессию
    :return:
    """
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session
    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture(scope="session")
def super_admin(user_session):
    """
    Создает юзер-сессию с правами супер-админа
    :param user_session:
    :return:
    """
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        "[SUPER_ADMIN]",
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    """
    Создает пользовательские данные
    :param test_user:
    :return:
    """
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """
    Создает сессию с правами обычного юзера
    :param user_session:
    :param super_admin:
    :param creation_user_data:
    :return:
    """
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        list(Roles.USER.value),
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def registration_user_data():
    """
    TBD
    :return:
    """
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

# ====================================================DataBases===============================================
@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)