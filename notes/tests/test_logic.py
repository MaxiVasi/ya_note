# В файле test_logic.py:
# Залогиненный пользователь может создать заметку, а анонимный — не может.
# Невозможно создать две заметки с одинаковым slug.
# Если при создании заметки не заполнен slug, то он формируется автоматически,
# с помощью функции pytils.translit.slugify.
# Пользователь может редактировать и удалять свои заметки,
# но не может редактировать или удалять чужие.

from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesCreation(TestCase):
    TITLE = 'Тестовое название заметки'
    TEXT = 'Тестовый текст заметки'
    SLUG = 'тестовое'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user_author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(title='Заголовок', text='Текст')
        # Адрес страницы с новостью.
        cls.url = reverse('notes:detail', args=(cls.note.slug,))
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Крокодил')
        
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'text': cls.COMMENT_TEXT} 

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.     
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        comments_count = Comment.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(comments_count, 0) 

    def test_user_can_create_comment(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, f'{self.url}#comments')
        # Считаем количество комментариев.
        comments_count = Comment.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(comments_count, 1)
        # Получаем объект комментария из базы.
        comment = Comment.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(comment.text, self.COMMENT_TEXT)
        self.assertEqual(comment.news, self.news)
        self.assertEqual(comment.author, self.user) 