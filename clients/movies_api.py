
from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, BASE_URL, MOVIES, MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester
from clients.auth_api import AuthAPI

class MoviesAPI(CustomRequester):
    """
    Класс для работы со списком фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)


    def get_movies(self, expected_status=200, **kwargs, ):
        """
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        print(self.headers)
        return self.send_request(
            method="GET",
            endpoint=MOVIES,
            expected_status=expected_status,
            query=kwargs,
            need_logging=True
        )

    def create_movie(self, test_movie=None, expected_status=201):
        """
        Создание нового фильма
        """

        return self.send_request(
            method="POST",
            endpoint=MOVIES,
            expected_status=expected_status,
            need_logging=True,
            data=test_movie
        )

    def delete_movie(self, test_movie, expected_status=200):
        #Создаем новый фильм
        create_movie = self.send_request(
            method="POST",
            endpoint=MOVIES,
            expected_status=201,
            need_logging=True,
            data=test_movie
        )

        #Получаем айди созданного фильма
        create_movie_response = create_movie.json()
        movie_id = create_movie_response["id"]

        #Удаляем созданный фильм nahooi
        return self.send_request(
        method = "DELETE",
        endpoint = f'{MOVIES}/{movie_id}',
        expected_status = expected_status,
        need_logging = True
        )

    def patch_movie(self, test_movie, updated_test_movie, expected_status):
        # Создаем новый фильм
        create_movie = self.send_request(
            method="POST",
            endpoint=MOVIES,
            expected_status=201,
            need_logging=True,
            data=test_movie
        )

        # Получаем айди созданного фильма
        create_movie_response = create_movie.json()
        movie_id = create_movie_response["id"]

        # Обновляем созданный фильм
        return self.send_request(
            method="PATCH",
            endpoint=f'{MOVIES}/{movie_id}',
            expected_status=expected_status,
            need_logging=True,
            data=updated_test_movie
        )