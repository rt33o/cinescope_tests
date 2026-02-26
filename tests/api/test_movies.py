from http.client import responses

import pytest
import requests


from tests.api.api_manager import ApiManager



class TestMovies:
    # # ==============================Получение афиш фильмов==============================
    # def test_get_movies(self, api_manager: ApiManager):
    #     max_price, min_price = 3000, 1000
    #     response = api_manager.movies_api.get_movies(maxPrice=max_price, minPrice=min_price, pageSize=1)
    #     response_data = response.json()
    #     movies = response_data['movies']
    #     price = movies[0]["price"]
    #     assert min_price < price < max_price, "Неверно приходят цены"
    #
    # def test_negative_invalid_page_size_get_movies(self, api_manager: ApiManager):
    #     page_size = 21
    #     response = api_manager.movies_api.get_movies(expected_status=400, pageSize=page_size)
    #     response_data = response.json()
    #     assert response_data['error'] == 'Bad Request', 'Неверная ошибка'


    # # ==============================Создание фильмов==============================
    # def test_create_movie(self, authorized_api_manager: ApiManager, test_movie):
    #     response = authorized_api_manager.movies_api.create_movie(test_movie=test_movie)
    #     response_data = response.json()
    #     assert response_data["name"] == test_movie["name"], "Имя созданного фильма не совпадает со значением, указанным при создании"
    #     assert response_data['id'], "Не присвоен айди"
    #
    # def test_negative_create_movie(self, api_manager: ApiManager, test_movie):
    #     response = api_manager.movies_api.create_movie(expected_status=401, test_movie=test_movie)
    #     response_data = response.json()
    #     assert response_data['message'] == "Unauthorized"
    #
    # ==============================Получение афиш фильмов по идентификатору==============================
    # def test_get_movies_by_id(self, authorized_api_manager: ApiManager):
    #     identification = 899
    #     response = authorized_api_manager.movies_api.get_movies_by_id(identification=identification)
    #     response_data = response.json()
    #     assert response_data['id'] == identification, 'Пришел неверный id'
    #
    # def test_negative_get_movies_by_non_exist_id(self, authorized_api_manager: ApiManager):
    #     identification = 0
    #     response = authorized_api_manager.movies_api.get_movies_by_id(expected_status=404, identification=identification)
    #     response_data = response.json()
    #     assert response_data['message'] == "Фильм не найден", 'Найден фильм по несуществующему ID'
    # #
    #
    #
    # ==============================Удаление фильмов==============================
    # def test_delete_movie(self, authorized_api_manager: ApiManager, movie_factory):
    #     movie = movie_factory()
    #     movie_id = movie["id"]
    #     response = authorized_api_manager.movies_api.delete_movie(movie_id=movie_id, expected_status=200)
    #     response_data = response.json()
    #     assert response_data['id'] == movie_id, 'Удален не тот фильм'
    #
    #
    # def test_negative_delete_movie(self, api_manager: ApiManager, movie_factory):
    #     response = api_manager.movies_api.delete_movie(movie_id=None, expected_status=404)
    #
    #     response_data = response.json()
    #     assert response_data["message"] == "Фильм не найден", 'Попытка удаления фильма '



    # ==============================Обновление фильмов==============================
    def test_update_movie(self, authorized_api_manager: ApiManager, movie_factory, updated_test_movie_data):
        movie = movie_factory()
        movie_id = movie["id"]
        response = authorized_api_manager.movies_api.patch_movie(movie_id=movie_id, updated_test_movie_data=updated_test_movie_data, expected_status=200)
        response_data = response.json()
        assert response_data["price"] != movie["price"], "Информация не была обновлена"
        assert response_data["name"] != movie["name"], "Description не должен был перезаписаться"
        assert response_data["imageUrl"] == movie['imageUrl'], 'ImageURL не должен был перезаписаться'

    # ==============================Обновление фильмов==============================
    def test_negative_invalid_id_update_movie(self, authorized_api_manager: ApiManager, movie_factory, updated_test_movie_data):
        movie = movie_factory()
        movie_id = None
        response = authorized_api_manager.movies_api.patch_movie(movie_id=movie_id, updated_test_movie_data=updated_test_movie_data, expected_status=404)
        response_data = response.json()
        assert response_data["message"] == "Фильм не найден", "Попытка обновления информации с невалидным ID"

