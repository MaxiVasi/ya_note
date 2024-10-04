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

from .fixture import BaseTestFixture

User = get_user_model()


class TestRoutes(BaseTestFixture):
    def test_home_page(self):
        """Проверка доступа к главной странице для пользователя."""
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        """Проверка доступа к страницам для обычного пользователя."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """Проверка доступа к страницам для авторизированного пользователя."""
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        """Проверка доступа к страницам редактирования и удаления заметки."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректов для анонимного пользователя."""
        for name in ('notes:detail',
                     'notes:edit',
                     'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_other_pages(self):
        """Проверка редиректов для анонимного пользователя."""
        for name in ('notes:list',
                     'notes:add',
                     'notes:success',
                     ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
