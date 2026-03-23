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
        self.auth_api = AuthAPI(session)
        self.user_api = UsersApi(session)
        self.movies_api = MoviesAPI(session)

    def close_session(self):
        self.session.close()