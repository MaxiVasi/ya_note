# В файле test_routes.py для проекта ya_note:
# 1 - Главная страница доступна анонимному пользователю.
# 2 - Аутентифицированному пользователю доступна страница со списком заметок notes/, 
# страница успешного добавления заметки done/, страница добавления новой заметки add/.
# 3 - Страницы отдельной заметки, удаления и редактирования заметки доступны только автору заметки.
# Если на эти страницы попытается зайти другой пользователь — вернётся ошибка 404.
# 4 - При попытке перейти на страницу списка заметок,
# страницу успешного добавления записи, страницу добавления заметки,
# отдельной заметки, редактирования или удаления заметки анонимный пользователь перенаправляется на страницу логина.
# 5 - Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны всем пользователям.
# Запуск тестов  python manage.py test notes.tests.test_routes -v 3

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.fixture import BaseTestFixture

User = get_user_model()


class TestRoutes(BaseTestFixture):
    def test_home_page(self):
        """Проверка доступа к главной странице для пользователя."""
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        """Проверка доступа к страницам для обычного пользователя."""
        urls = (
            (self.HOME_URL),
            (self.LOGIN_URL),
            (self.LOGOUT_URL),
            (self.SIGNUP_URL),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """Проверка доступа к страницам для авторизированного пользователя."""
        urls = (
            (self.ADD_URL),
            (self.LIST_URL),
            (self.SUCCESS_URL),
        )
        for name in urls:
            with self.subTest(user=self.author, name=name):
                response = self.author_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        """Проверка доступа к страницам редактирования и удаления заметки."""
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (self.DETAILS_URL, self.EDITS_URL, self.DELETES_URL):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректов для анонимного пользователя."""
        for name in (self.DETAILS_URL, self.EDITS_URL, self.DELETES_URL):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_other_pages(self):
        """Проверка редиректов для анонимного пользователя."""
        for name in (self.LIST_URL, self.ADD_URL, self.SUCCESS_URL):
            with self.subTest(name=name):
                redirect_url = f'{self.LOGIN_URL}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
