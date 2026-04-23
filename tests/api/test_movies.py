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
    @pytest.mark.smoke
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

    @pytest.mark.negative
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
    @pytest.mark.smoke
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
    @pytest.mark.integration
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
    @pytest.mark.negative
    def test_negative_unathorized_user_create_movie(self, common_user, test_movie):
        movie_name = test_movie.get("name", "Unknown")
        with allure.step(f"Попытка создания фильма '{movie_name}' обычным пользователем"):
            # Мы передаем expected_status=403, так как это ожидаемое поведение
            response = common_user.api.movies_api.create_movie(
                test_movie=test_movie,
                expected_status=403,
                need_logging=False
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
    @pytest.mark.negative
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
    @allure.title("Получение информации о фильме по ID")
    @allure.description("""
        Тест проверяет корректность получения данных конкретного фильма:
        1. Отправляем GET-запрос на получение фильма по ID {identification}.
        2. Проверяем, что ID в теле ответа совпадает с запрашиваемым.
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_movies_by_id(self, authorized_api_manager: ApiManager):
        identification = 899

        with allure.step(f"Запрос информации о фильме с ID: {identification}"):
            response = authorized_api_manager.movies_api.get_movies_by_id(
                identification=identification,
                model=GettingMovieById
            )

        with allure.step("Проверка соответствия ID в ответе"):
            assert response.id == identification, (
                f"Ошибка: ожидался ID {identification}, но пришел {response.id}"
            )

    @pytest.mark.negative
    @allure.title("Негативный тест: получение фильма по несуществующему ID (404 Not Found)")
    @allure.description("""
        Проверка обработки запроса к отсутствующему ресурсу:
        1. Отправляем GET-запрос с ID = {identification} (заведомо несуществующий).
        2. Ожидаем статус-код 404.
        3. Проверяем наличие корректного сообщения об ошибке: 'Фильм не найден'.
        """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_negative_get_movies_by_non_exist_id(self, authorized_api_manager: ApiManager):
        identification = 0

        with allure.step(f"Запрос фильма с ID: {identification}"):
            response = authorized_api_manager.movies_api.get_movies_by_id(
                expected_status=404,
                identification=identification
            )
            response_data = response.json()

        with allure.step("Проверка сообщения об ошибке в ответе"):
            assert response_data['message'] == "Фильм не найден", (
                f"Ошибка: ожидалось сообщение 'Фильм не найден', но пришло: {response_data.get('message')}"
            )



    # ==============================Удаление фильмов==============================
    @allure.title("Удаление фильма (права Супер-админа)")
    @allure.description("""
        Проверка удаления фильма с полными правами доступа:
        1. Генерируем новый фильм через factory.
        2. Отправляем запрос на удаление созданного фильма по его ID.
        3. Проверяем, что API подтверждает удаление именно этого ID.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    @pytest.mark.regression
    def test_delete_movie(self, super_admin, movie_factory):
        with allure.step("Предусловие: Создание тестового фильма"):
            movie = movie_factory()
            movie_id = movie["id"]
            movie_name = movie.get("name", "Unknown")

            with allure.step(f"Действие: Удаление фильма '{movie_name}' (ID: {movie_id})"):
                response = super_admin.api.movies_api.delete_movie(
                    movie_id=movie_id,
                    expected_status=200,
                    model=DeleteMovie
                )

            with allure.step("Проверка: в ответе вернулся ID удаленного фильма"):
                assert response.id == movie_id, (
                    f"Ошибка: ожидалось удаление ID {movie_id}, но в ответе пришел {response.id}"
                )

    @allure.title("Негативный тест: удаление фильма без указания ID (404 Not Found)")
    @allure.description("""
        Проверка обработки некорректного ID при удалении:
        1. Отправляем запрос на удаление с movie_id = None.
        2. Ожидаем, что сервер не найдет ресурс и вернет 404.
        3. Проверяем наличие сообщения 'Фильм не найден'.
        """)
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    def test_negative_delete_movie(self, super_admin):
        with allure.step("Попытка удаления фильма с ID: None"):
            response = super_admin.api.movies_api.delete_movie(
                movie_id=None,
                expected_status=404
            )
            response_data = response.json()

        with allure.step("Проверка сообщения об ошибке"):
            assert response_data["message"] == "Фильм не найден", (
                f"Ожидалось 'Фильм не найден', но пришло: {response_data.get('message')}"
            )


    # ==============================Обновление фильмов==============================
    @allure.title("Частичное обновление данных фильма (PATCH)")
    @allure.description("""
        Тест проверяет корректность обновления информации о фильме:
        1. Создаем тестовый фильм через factory.
        2. Отправляем PATCH-запрос с новыми данными (цена и название).
        3. Проверяем, что в ответе от API значения полей изменились по сравнению с исходными.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    @pytest.mark.regression
    def test_update_movie(self, authorized_api_manager: ApiManager, movie_factory, updated_test_movie_data):
        with allure.step("Предусловие: Создание фильма для последующего обновления"):
            movie = movie_factory()
            movie_id = movie["id"]
            old_name = movie["name"]
            old_price = movie["price"]

        with allure.step(f"Действие: Обновление фильма ID {movie_id} новыми данными"):
            response = authorized_api_manager.movies_api.patch_movie(
                movie_id=movie_id,
                data=updated_test_movie_data,
                expected_status=200,
                model=UpdateMovie
            )

            allure.attach(str(updated_test_movie_data), name="Update Payload",
                          attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка: Данные успешно изменены"):
            # Проверяем изменение цены
            assert response.price != old_price, (
                f"Ошибка: цена не изменилась и осталась {old_price}"
            )
            # Проверяем изменение имени
            assert response.name != old_name, (
                f"Ошибка: имя не было обновлено (текущее: {response.name}, старое: {old_name})"
            )



    @allure.title("Негативный тест: обновление фильма с ID=None (404 Not Found)")
    @allure.description("""
        Проверка валидации идентификатора при частичном обновлении:
        1. Попытка отправить PATCH-запрос с movie_id = None.
        2. Ожидаем, что сервер вернет 404 Not Found.
        3. Проверяем корректность сообщения об ошибке 'Фильм не найден'.
        """)
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    def test_negative_invalid_id_update_movie(self, authorized_api_manager: ApiManager, updated_test_movie_data):
        movie_id = None

        with allure.step(f"Попытка обновления фильма с ID: {movie_id}"):
            response = authorized_api_manager.movies_api.patch_movie(
                movie_id=movie_id,
                data=updated_test_movie_data,
                expected_status=404
            )
            response_data = response.json()

        with allure.step("Проверка сообщения об ошибке"):
            assert response_data["message"] == "Фильм не найден", (
                f"Ожидалось сообщение 'Фильм не найден', но пришло: {response_data.get('message')}"
            )

