from constants.constants import MOVIES, MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    """
    Класс для работы со списком фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)

    def request_and_validate(self, method, endpoint, model=None,  expected_status=200, need_logging=False, **kwargs):
        # kwargs здесь могут содержать json, params, headers для send_request
        response = self.send_request(
            method=method,
            endpoint=endpoint,
            expected_status=expected_status,
            need_logging=need_logging,
            **kwargs
        )

        if model and response.status_code == expected_status:
            return model(**response.json())
        return response

    def get_movies(self, expected_status=200, model=None, **kwargs):
        return self.request_and_validate(
            "GET", MOVIES, model=model, expected_status=expected_status, query=kwargs
        )

    # def get_movies(self, expected_status=200, model=None, **kwargs, ):
    #     """
    #     Получить список фильмов (GET /movies) с query-параметрами.
    #     :param expected_status: Ожидаемый статус-код.
    #     :param model: Pydantic модель валидации данных.
    #     :param kwargs: Query-параметры запроса.
    #     """
    #
    #     response = self.send_request(
    #         method="GET",
    #         endpoint=MOVIES,
    #         expected_status=expected_status,
    #         query=kwargs,
    #         need_logging=False
    #     )
    #
    #     if model and expected_status == 200:
    #         return model(**response.json())
    #
    #     return response

    def get_movies_by_id(self, expected_status=200, identification=1, model=False, need_logging=False):
        """
        Получить фильм по id (GET /movies/{id}).
        :param need_logging:
        :param model:
        :param identification: ID фильма.
        :param expected_status: Ожидаемый статус-код.
        :param передаваемая для валидации модель
        """
        return self.request_and_validate(
            "GET", endpoint=f'{MOVIES}/{identification}', model=model, expected_status=expected_status, need_logging=need_logging
        )




    def create_movie(self, test_movie=None, expected_status=201, model=None, need_logging=False):
        """
        Создать новый фильм (POST /movies).
        :param model:
        :param test_movie: Тело запроса (данные фильма).
        :param expected_status: Ожидаемый статус-код.
        :param need_logging: Включить логирование запроса/ответа.
        """

        return self.request_and_validate(
            "POST", MOVIES, model=model, expected_status=expected_status, data=test_movie, need_logging=need_logging
        )

        # return self.send_request(
        #     method="POST",
        #     endpoint=MOVIES,
        #     expected_status=expected_status,
        #     need_logging=need_logging,
        #     data=test_movie
        # )

    def delete_movie(self, movie_id=None, model=None, expected_status=200):
        """
        Удалить фильм по id (DELETE /movies/{id}).
        :param model:
        :param movie_id: ID фильма для удаления.
        :param expected_status: Ожидаемый статус-код.
        :param передаваемая для валидации модель
        """

        return self.request_and_validate(
            "DELETE", endpoint = f'{MOVIES}/{movie_id}', model=model, expected_status=expected_status, need_logging=False
        )



    def patch_movie(self, movie_id, data, model=None, expected_status=200):
        """
        Частично обновить фильм по id (PATCH /movies/{id}).
        :param movie_id: ID фильма.
        :param data: Данные для обновления (тело запроса).
        :param expected_status: Ожидаемый статус-код.
        :param model передаваемая для валидации модель
        """
        # Обновляем созданный фильм
        return self.request_and_validate(
            "PATCH", endpoint=f'{MOVIES}/{movie_id}', data=data, model=model, expected_status=expected_status, need_logging=False
        )


