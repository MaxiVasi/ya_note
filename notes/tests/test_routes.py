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

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='user_reader')
        cls.author = User.objects.create(username='user_author')
        cls.note = Note.objects.create(
            title='Тестовое название заметки',
            text='Тестовый текст заметки',
            author=cls.author,
        )

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    """Проверка доступа к страницам для неавторизированного пользователя."""
    def test_pages_availability(self):
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

    """Проверка доступа к страницам для авторизированного пользователя."""
    def test_pages_availability_for_author(self):
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

    """Проверка доступа к страницам редактирования и удаления заметки."""
    def test_availability_for_notes_edit_and_delete(self):
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

    """Проверка редиректов для анонимного пользователя."""
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:detail',
                     'notes:edit',
                     'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    """Проверка редиректов для анонимного пользователя."""
    def test_redirect_for_anonymous_client_other_pages(self):
        login_url = reverse('users:login')
        for name in ('notes:list',
                     'notes:add',
                     'notes:success',
                     ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
