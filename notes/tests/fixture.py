from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class BaseTestFixture(TestCase):
    TITLE = 'Тестовое название заметки'
    TEXT = 'Тестовый текст заметки'
    NEW_TEXT = 'Новый текст заметки'
    SLUG = 'тестовое'
    ADD_URL = reverse('notes:add')
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    LIST_URL = reverse('notes:list')
    DETAILS_URL = 'notes:detail'
    EDITS_URL = 'notes:edit'
    DELETES_URL = 'notes:delete'

    @classmethod
    def setUpTestData(cls):
        cls.data = {'title': 'Новый', 'text': 'Текст'}
        cls.reader = User.objects.create(username='user_reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='user_author')
        cls.newtextdata = {'title': cls.TITLE,
                           'text': cls.NEW_TEXT, 'author': cls.author}
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=slugify(cls.TITLE),
        )
        cls.author_1 = User.objects.create(username='user_author_1')
        cls.auth_client_1 = Client()
        cls.auth_client_1.force_login(cls.author_1)
        cls.note_1 = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author_1,
            slug=slugify(cls.TITLE) + '1',
        )
