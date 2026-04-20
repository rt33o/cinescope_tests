from faker import Faker
import pytest
import requests
from constants import constants
from constants.roles import Roles
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from tests.api.api_manager import ApiManager
from resources.user_creds import SuperAdminCreds
from entities.user import User
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
import json
import allure

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
    db_session.rollback()
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


@pytest.fixture(scope="function")
def created_test_movie(db_helper):
    """
    Фикстура: создает тестовый фильм напрямую в БД через DataGenerator
     и удаляет его после завершения теста.
    """
    # 1. Генерируем данные для фильма
    movie_data = DataGenerator.generate_random_movie()

    # 2. Создаем фильм в базе через db_helper
    movie = db_helper.create_test_movie(movie_data)

    # 3. Отдаем объект фильма в тест
    yield movie

    # 4. Cleanup: Удаляем фильм после теста, если он еще существует
    if db_helper.get_movie_by_id(movie.id):
        db_helper.delete_movie_by_id(movie.id)


# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     # Выполняем тест
#     outcome = yield
#     report = outcome.get_result()
#
#     # Если тест упал именно во время выполнения (фаза 'call')
#     if report.failed:
#         # Ищем наш менеджер среди фикстур теста
#         # Он может называться api_manager или authorized_api_manager
#         manager = None
#         for fixture_name in ["api_manager", "authorized_api_manager"]:
#             if fixture_name in item.funcargs:
#                 manager = item.funcargs[fixture_name]
#                 break
#
#         if manager and hasattr(manager, "last_response") and manager.last_response is not None:
#             response = manager.last_response
#
#             # Прикрепляем ответ к Allure
#             try:
#                 # Если это JSON, крепим красиво со всеми отступами
#                 allure.attach(
#                     json.dumps(response.json(), indent=4, ensure_ascii=False),
#                     name="API_RESPONSE_ON_FAILURE",
#                     attachment_type=allure.attachment_type.JSON
#                 )
#             except Exception:
#                 # Если там не JSON (например, 500 ошибка с HTML), крепим как текст
#                 allure.attach(
#                     response.text,
#                     name="API_RESPONSE_BODY_TEXT",
#                     attachment_type=allure.attachment_type.TEXT
#                 )
#
#             # Дополнительно можно прикрепить и URL запроса
#             allure.attach(
#                 f"Method: {response.request.method}\nURL: {response.request.url}",
#                 name="API_REQUEST_INFO",
#                 attachment_type=allure.attachment_type.TEXT
#             )