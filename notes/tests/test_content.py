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


class TestContent(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    TITLE = 'Тестовое название заметки'
    TEXT = 'Тестовый текст заметки'
    SLUG = 'тестовое'
    LIST_URLS = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаем в базе - 2 записи от имени автора и автора_1."""
        cls.author = User.objects.create(username='user_author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=slugify(cls.TITLE),
        )
        cls.author_1 = User.objects.create(username='user_author_1')
        cls.note_1 = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author_1,
            slug=slugify(cls.TITLE) + '1',
        )

    def test_notes_creation_by_author(self):
        """Проверка что запись автора есть на старнице записей автора."""
        response = self.author_client.get(self.LIST_URLS)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_in_list_from_another_author(self):
        """Проверка что запись автора_1 нет на старнице записей автора."""
        response = self.author_client.get(self.LIST_URLS)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_1, object_list)

    def test_notes_count(self):
        """Проверяем что на странице автора есть только 1 заметка!"""
        response = self.author_client.get(self.LIST_URLS)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)

    def test_authorized_client_has_form_on_edit_page(self):
        """Проверяем что на странице редактирования заметки есть форма!"""
        edit_urls = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.get(edit_urls)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_on_add_page(self):
        """Проверяем что на странице добавления заметки есть форма!"""
        add_urls = reverse('notes:add')
        response = self.author_client.get(add_urls)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
