from tests.api.api_manager import ApiManager
import pytest
from resources.test_data import MOVIES_FILTER_DATA
from models.movies_models import GettingMovies, CreateMovie, GettingMovieById, DeleteMovie, UpdateMovie
import allure

class TestMovies:


    # ==============================Получение афиш фильмов==============================
    @allure.title("Проверка фильтрации афиши по цене: от {min_p} до {max_p}")
    @allure.description("Проверяем, что при применении фильтров API возвращает фильмы, цена которых попадает в диапазон.")
    @pytest.mark.parametrize("min_p, max_p, location, genre_id", MOVIES_FILTER_DATA)
    def test_get_movies(self, api_manager: ApiManager, min_p, max_p, location, genre_id):
        with allure.step(f"Запрос списка фильмов (Цена: {min_p}-{max_p}, Локация: {location}, Жанр: {genre_id})"):
            response = api_manager.movies_api.get_movies(
                model=GettingMovies,
                maxPrice=max_p,
                minPrice=min_p,
                locations=location,
                genreId=genre_id,
                pageSize=3
            )

            # Прикрепляем ответ для истории
            allure.attach(
                str(response),
                name="API Response",
                attachment_type=allure.attachment_type.JSON
            )
        with allure.step("Проверка цены первого фильма в выдаче"):
            assert len(response.movies) > 0, "Результаты поиска пусты, невозможно проверить цену"

            first_movie = response.movies[0]
            price = first_movie.price

            assert min_p < price < max_p, f"Цена {price} вне диапазона {min_p}-{max_p}"

    @pytest.mark.slow
    @allure.title("Негативный тест: получение афиши с некорректным pageSize")
    @allure.description("""
        Тест проверяет валидацию параметра pageSize:
        1. Устанавливаем pageSize = 21 (превышение допустимого лимита).
        2. Ожидаем, что API вернет статус-код 400 и текст ошибки 'Bad Request'.
        """)
    def test_negative_invalid_page_size_get_movies(self, api_manager: ApiManager):
        page_size = 21

        with allure.step(f"Запрос списка фильмов с недопустимым pageSize = {page_size}"):
            response = api_manager.movies_api.get_movies(
                expected_status=400,
                pageSize=page_size
            )

            # Логируем тело ответа, чтобы видеть структуру ошибки от бэкенда
            response_data = response.json()
            allure.attach(
                str(response_data),
                name="Error Response Body",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Проверка сообщения об ошибке в ответе"):
            assert response_data['error'] == 'Bad Request', (
                f"Ожидалась ошибка 'Bad Request', но пришло: {response_data.get('error')}"
            )


    # ==============================Создание фильмов==============================
    @allure.title("Успешное создание фильма через API")
    @allure.description("""
        Позитивный сценарий:
        1. Отправляем POST-запрос на создание фильма с валидными данными.
        2. Проверяем, что в ответе API имя фильма соответствует отправленному.
        """)
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_movie(self, authorized_api_manager: ApiManager, test_movie):
        expected_name = test_movie["name"]

        with allure.step(f"Отправка запроса на создание фильма: {expected_name}"):
            response = authorized_api_manager.movies_api.create_movie(
                model=CreateMovie,
                test_movie=test_movie
            )

            # Логируем отправленные данные и ответ
            allure.attach(
                str(test_movie),
                name="Request Data",
                attachment_type=allure.attachment_type.JSON
            )
            allure.attach(
                str(response),
                name="Response Model",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Сверка имени созданного фильма"):
            assert response.name == expected_name, (
                f"Ошибка: ожидалось имя '{expected_name}', но API вернул '{response.name}'"
            )




    @allure.title("Проверка полного цикла: создание и удаление фильма (API + БД)")
    @allure.description("""
            Тест проверяет:
            1. Отсутствие фильма в БД до начала теста.
            2. Появление фильма в БД после создания через API.
            3. Исчезновение фильма из БД после удаления через API.
            """)
    def test_movie_full_db_lifecycle(self, authorized_api_manager, db_helper, test_movie):
        """
        Проверка жизненного цикла фильма в БД через API
        """
        movie_name = test_movie["name"]

        with allure.step(f"Предусловие: проверка отсутствия фильма '{movie_name}' в БД"):
            movie_before = db_helper.get_movie_by_name(movie_name)
            assert movie_before is None, f"Фильм {movie_name} уже существует в базе"

        with allure.step("Действие: Создание фильма через API"):
            response = authorized_api_manager.movies_api.create_movie(
                test_movie=test_movie
            )
            # Логируем ответ API прямо в отчет Allure
            allure.attach(
                str(response.json()),
                name="API Response Body",
                attachment_type=allure.attachment_type.JSON
            )

            movie_id = response.json().get("id")
            assert movie_id is not None, "API не вернул ID созданного фильма"

        with allure.step(f"Проверка: Фильм с ID {movie_id} появился в БД"):
            movie_in_db = db_helper.get_movie_by_id(movie_id)
            assert movie_in_db is not None, "Фильм не найден в БД после создания"
            assert movie_in_db.name == movie_name, f"Ожидалось имя {movie_name}, но в БД {movie_in_db.name}"

        with allure.step(f"Действие: Удаление фильма с ID {movie_id} через API"):
            authorized_api_manager.movies_api.delete_movie(movie_id=movie_id)

        with allure.step(f"Проверка: Фильм с ID {movie_id} удален из БД"):
            movie_after = db_helper.get_movie_by_id(movie_id)
            assert movie_after is None, f"Фильм с ID {movie_id} все еще остался в БД после удаления"


    @allure.title("Негативный тест: создание фильма пользователем без прав (403 Forbidden)")
    @allure.description("""
        Проверка прав доступа:
        1. Авторизуемся под обычным пользователем (без прав администратора).
        2. Пытаемся отправить запрос на создание фильма.
        3. Ожидаем, что API заблокирует действие и вернет статус 403 Forbidden.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    def test_negative_unathorized_user_create_movie(self, common_user, test_movie):
        movie_name = test_movie.get("name", "Unknown")
        with allure.step(f"Попытка создания фильма '{movie_name}' обычным пользователем"):
            # Мы передаем expected_status=403, так как это ожидаемое поведение
            response = common_user.api.movies_api.create_movie(
                test_movie=test_movie,
                expected_status=403
            )

            allure.attach(
                f"User: Common User\nMovie Data: {test_movie}",
                name="Request Context",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка: доступ запрещен (статус 403)"):
            assert response.status_code == 403, (
                f"Ожидался статус 403, но получен {response.status_code}"
            )

    @allure.title("Негативный тест: создание фильма без авторизации (401 Unauthorized)")
    @allure.description("""
        Проверка системы аутентификации:
        1. Попытка создать фильм через API без передачи токена/авторизации.
        2. Ожидаем, что сервер отклонит запрос со статусом 401.
        3. Проверяем, что в ответе содержится сообщение 'Unauthorized'.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    def test_negative_create_movie(self, api_manager: ApiManager, test_movie):
        with allure.step("Запрос на создание фильма неавторизованным пользователем"):
            response = api_manager.movies_api.create_movie(
                expected_status=401,
                test_movie=test_movie
            )
            response_data = response.json()

            # Прикрепляем ответ для истории
            allure.attach(
                str(response_data),
                name="Unauthorized Response Body",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Проверка сообщения в теле ответа"):
            assert response_data['message'] == "Unauthorized", (
                f"Ожидалось сообщение 'Unauthorized', но получено: {response_data.get('message')}"
            )

    # ==============================Получение афиш фильмов по идентификатору==============================
    def test_get_movies_by_id(self, authorized_api_manager: ApiManager):
        identification = 899
        response = authorized_api_manager.movies_api.get_movies_by_id(identification=identification, model=GettingMovieById)
        assert response.id == identification, 'Пришел неверный id'

    @pytest.mark.slow
    def test_negative_get_movies_by_non_exist_id(self, authorized_api_manager: ApiManager):
        identification = 0
        response = authorized_api_manager.movies_api.get_movies_by_id(expected_status=404, identification=identification)
        response_data = response.json()
        assert response_data['message'] == "Фильм не найден", 'Найден фильм по несуществующему ID'
    #


    # ==============================Удаление фильмов==============================
    @pytest.mark.slow
    def test_delete_movie(self, super_admin, movie_factory):
        movie = movie_factory()
        movie_id = movie["id"]
        response = super_admin.api.movies_api.delete_movie(movie_id=movie_id, expected_status=200, model=DeleteMovie)
        response_data = response.json()
        assert response.id == movie_id, 'Удален не тот фильм'


    def test_negative_delete_movie(self, api_manager: ApiManager, movie_factory):
        response = api_manager.movies_api.delete_movie(movie_id=None, expected_status=404)

        response_data = response.json()
        assert response_data["message"] == "Фильм не найден", 'Попытка удаления фильма '



    # ==============================Обновление фильмов==============================
    @pytest.mark.slow
    def test_update_movie(self, authorized_api_manager: ApiManager, movie_factory, updated_test_movie_data):
        movie = movie_factory()
        movie_id = movie["id"]
        response = authorized_api_manager.movies_api.patch_movie(movie_id=movie_id, data=updated_test_movie_data, expected_status=200, model=UpdateMovie)
        # response_data = response.json()
        # assert response_data["price"] != movie["price"], "Информация не была обновлена"
        # assert response_data["name"] != movie["name"], "Description не должен был перезаписаться"
        # assert response_data["imageUrl"] == movie['imageUrl'], 'ImageURL не должен был перезаписаться'

    # ==============================Обновление фильмов==============================
    def test_negative_invalid_id_update_movie(self, authorized_api_manager: ApiManager, movie_factory, updated_test_movie_data):
        movie = movie_factory()
        movie_id = None
        response = authorized_api_manager.movies_api.patch_movie(movie_id=movie_id, data=updated_test_movie_data, expected_status=404)
        response_data = response.json()
        assert response_data["message"] == "Фильм не найден", "Попытка обновления информации с невалидным ID"

