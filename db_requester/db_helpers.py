from sqlalchemy.orm import Session
from db_models.user import UserDBModel
from db_models.movies import MovieDBModel
from datetime import datetime
import random



class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()


    # '''
    # Пример хелпера для movies
    # def get_movie_by_id(self, movie_id: str):
    #     """Получает фильм по ID"""
    #     return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()
    # '''
    def create_test_movie(self, movie_data: dict) -> MovieDBModel:
        """Создает фильм, переводя ключи из camelCase в snake_case"""



    # Создаем новый словарь с правильными ключами для БД
        mapped_data = {
            "id": movie_data.get("id") or random.randint(100000, 9999999),
            "name": movie_data.get("name"),
            "price": movie_data.get("price") or 0,
            "description": movie_data.get("description"),
            "image_url": movie_data.get("imageUrl") or movie_data.get("image_url"),
            "location": movie_data.get("location"),
            "published": movie_data.get("published") or False,
            "rating": movie_data.get("rating") or 5.0,  # ЗАПЛАТКА: если рейтинга нет, ставим 5.0
            "genre_id": str(movie_data.get("genreId") or movie_data.get("genre_id") or "1"),
            "created_at": datetime.now()
        }

        print(mapped_data)

        # Убираем None значения, если генератор что-то не заполнил
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        try:
            movie = MovieDBModel(**mapped_data)
            self.db_session.add(movie)
            self.db_session.commit()
            self.db_session.refresh(movie)
            return movie
        except Exception as e:
            self.db_session.rollback() #Откат транзации если что-то пошло не так
            raise e

    def get_movie_by_id(self, movie_id: str) -> MovieDBModel:
        """Получает фильм по ID"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

    def get_movie_by_name(self, name: str) -> MovieDBModel:
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def movie_exists_by_id(self, movie_id: str) -> bool:
        """Проверяет существование фильма (возвращает True/False)"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).count() > 0

    def delete_movie_by_id(self, movie_id: str):
        """Удаляет фильм по ID"""
        movie = self.get_movie_by_id(movie_id)
        if movie:
            self.db_session.delete(movie)
            self.db_session.commit()