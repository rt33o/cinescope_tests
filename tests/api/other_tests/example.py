from tests.api.api_manager import ApiManager
import pytest



# ==============================Удаление фильмов==============================
def test_delete_movie(super_admin, movie_factory):
    movie = movie_factory()
    movie_id = movie["id"]
    response = super_admin.api.movies_api.delete_movie(movie_id=movie_id, expected_status=200)
    response_data = response.json()
    assert response_data['id'] == movie_id, 'Удален не тот фильм'