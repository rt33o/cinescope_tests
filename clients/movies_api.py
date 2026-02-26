
from constants import MOVIES, MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    """
    Класс для работы со списком фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)


    def get_movies(self, expected_status=200, **kwargs, ):
        """
        Получить список фильмов (GET /movies) с query-параметрами.
        :param expected_status: Ожидаемый статус-код.
        :param kwargs: Query-параметры запроса.
        """
        return self.send_request(
            method="GET",
            endpoint=MOVIES,
            expected_status=expected_status,
            query=kwargs,
            need_logging=False
        )

    def get_movies_by_id(self, expected_status=200, identification=1):
        """
        Получить фильм по id (GET /movies/{id}).
        :param identification: ID фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f'{MOVIES}/{identification}',
            expected_status=expected_status,
            need_logging=False
        )

    def create_movie(self, test_movie=None, expected_status=201, need_logging=False):
        """
        Создать новый фильм (POST /movies).
        :param test_movie: Тело запроса (данные фильма).
        :param expected_status: Ожидаемый статус-код.
        :param need_logging: Включить логирование запроса/ответа.
        """

        return self.send_request(
            method="POST",
            endpoint=MOVIES,
            expected_status=expected_status,
            need_logging=need_logging,
            data=test_movie
        )

    def delete_movie(self, movie_id=None, expected_status=200):
        """
        Удалить фильм по id (DELETE /movies/{id}).
        :param movie_id: ID фильма для удаления.
        :param expected_status: Ожидаемый статус-код.
        """


        #Удаляем созданный фильм
        return self.send_request(
        method = "DELETE",
        endpoint = f'{MOVIES}/{movie_id}',
        expected_status = expected_status,
        need_logging = True
        )

    def patch_movie(self, movie_id, updated_test_movie_data, expected_status):
        """
        Частично обновить фильм по id (PATCH /movies/{id}).
        :param movie_id: ID фильма.
        :param updated_test_movie_data: Данные для обновления (тело запроса).
        :param expected_status: Ожидаемый статус-код.
        """

        # Обновляем созданный фильм
        return self.send_request(
            method="PATCH",
            endpoint=f'{MOVIES}/{movie_id}',
            expected_status=expected_status,
            need_logging=True,
            data=updated_test_movie_data
        )