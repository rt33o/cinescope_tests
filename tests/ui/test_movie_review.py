import allure
import pytest
from models.page_object_models import CinescopLoginPage, CinescopMoviePage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Отзывов")
@pytest.mark.regression
class TestMovieReview:

    @allure.title("Успешное оставление отзыва под фильмом")
    def test_leave_review_successfully(self, page, registered_user):
        # Инициализируем страницы, передавая встроенную фикстуру page
        login_page = CinescopLoginPage(page)
        movie_page = CinescopMoviePage(page)

        # 1. Авторизация
        login_page.open()
        login_page.login(registered_user["email"], registered_user["password"])
        login_page.assert_was_redirect_to_home_page()

        # 2. Переход на страницу первого фильма
        movie_page.click_first_movie()

        # 3. Заполнение формы отзыва и отправка
        review_text = "Автотесты написаны, локаторы настроены, отзывы оставляются как надо"
        movie_page.leave_review(review_text)

        # 4. Проверка ассертов и снятие скриншота в Allure
        movie_page.assert_review_was_submitted()
        movie_page.make_screenshot_and_attach_to_allure()