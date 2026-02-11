from http.client import responses

import pytest
import requests


from constants import BASE_URL, HEADERS, MOVIES
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager


class TestMovies:
    # ==============================Получение афиш фильмов==============================
    def test_get_movies(self, api_manager: ApiManager):
        max_price, min_price = 3000, 1000
        response = api_manager.movies_api.get_movies(maxPrice=max_price, minPrice=min_price)
        response_data = response.json()

    def test_negative_get_movies(self, api_manager: ApiManager):
        pageSize = 21
        response = api_manager.movies_api.get_movies(exppected_status=400, pageSize=pageSize)
        response_data = response.json()


    # ==============================Создание фильмов==============================
    def test_create_movie(self, authorized_api_manager: ApiManager, test_movie):
        response = authorized_api_manager.movies_api.create_movie(test_movie=test_movie)
        response_data = response.json()
        assert response_data["name"] == test_movie["name"], "Имя созданного фильма не совпадает со значением, указанным при создании"
        assert response_data['id'], "Не присвоен айди"

    def test_negative_create_movie(self, api_manager: ApiManager, test_movie):
        response = api_manager.movies_api.create_movie(expected_status=401, test_movie=test_movie)
        response_data = response.json()

    # ==============================Удаление фильмов==============================
    def test_delete_movie(self, authorized_api_manager: ApiManager, test_movie):
        response = authorized_api_manager.movies_api.delete_movie(test_movie=test_movie)
        response_data = response.json()

    def test_negative_delete_movie(self, api_manager: ApiManager, test_movie):
        response = api_manager.movies_api.delete_movie(expected_status=401, test_movie=test_movie)
        response_data = response.json()

    # ==============================Обновление фильмов==============================
    def test_update_movie(self, authorized_api_manager: ApiManager, test_movie, updated_test_movie):
        response = authorized_api_manager.movies_api.patch_movie(test_movie=test_movie, updated_test_movie=updated_test_movie, expected_status=200)
        response_data = response.json()
        assert response_data["price"] != test_movie["price"], "Информация не была обновлена"
        assert response_data["description"] == test_movie["description"], "description не должен был перезаписаться"
        print(response_data)