from clients.auth_api import AuthAPI
from clients.user_api import UsersApi
from clients.movies_api import MoviesAPI

class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.
    """
    def __init__(self, session):
        """
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        """
        self.session = session
        self.last_response = None  # Сюда будем сохранять последний ответ

        # Обертка для метода request, чтобы он запоминал ответ
        original_request = self.session.request

        def wrapped_request(*args, **kwargs):
            response = original_request(*args, **kwargs)
            self.last_response = response  # Сохраняем ответ в "память" менеджера
            return response

        # Подменяем стандартный метод сессии на наш с памятью
        self.session.request = wrapped_request

        self.auth_api = AuthAPI(session)
        self.user_api = UsersApi(session)
        self.movies_api = MoviesAPI(session)

    def close_session(self):
        self.session.close()