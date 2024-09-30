# В файле test_content.py:
# Отдельная заметка передаётся на страницу со списком заметок в списке object_list в словаре context;
# В список заметок одного пользователя не попадают заметки другого пользователя;
# На страницы создания и редактирования заметки передаются формы.

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

from pytils.translit import slugify

User = get_user_model()


class TestContentList(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    TITLE = 'Тестовое название заметки'
    TEXT = 'Тестовый текст заметки'
    SLUG = 'тестовое'

    @classmethod
    def setUpTestData(cls):
        """Создаем в базе - 2 записи от имени автора и автора_1."""
        cls.author = User.objects.create(username='user_author')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=slugify(cls.TITLE),
        )
        cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.author_1 = User.objects.create(username='user_author_1')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author_1)
        cls.note_1 = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author_1,
            slug=slugify(cls.TITLE) + '1',
        )

    def test_notes_count(self):
        """Проверяем что на странице автора есть только 1 заметка!"""
        self.client.force_login(self.author)
        list_urls = reverse('notes:list')
        response = self.client.get(list_urls)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)

    def test_authorized_client_has_form_on_edit_page(self):
        """Проверяем что на странице редактирования заметки есть форма!"""
        self.client.force_login(self.author)
        edit_urls = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(edit_urls)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_on_add_page(self):
        """Проверяем что на странице добавления заметки есть форма!"""
        self.client.force_login(self.author)
        add_urls = reverse('notes:add')
        response = self.client.get(add_urls)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
