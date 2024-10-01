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
        """Создаем в базе - 2 записи от имени автора и автора_1."""
        cls.author = User.objects.create(username='user_author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=slugify(cls.TITLE),
        )
        cls.url_add = reverse('notes:add')

        cls.form_data = {'title': 'Новый', 'text': 'Текст'}
        cls.author_1 = User.objects.create(username='user_author_1')
        cls.note_1 = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author_1,
            slug=slugify(cls.TITLE) + '1',
        )

    def test_anonymous_user_cant_create_note(self):
        """Проверка - анонимный пользователь не может создать запись!"""
        self.client.post(self.url_add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_user_can_create_note(self):
        """Проверка - пользователь author может создать запись!"""
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 3)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, 'Новый')
        self.assertEqual(new_note.text, 'Текст')
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверка пользователь author не может удалить запись author_1!"""
        delete_url = reverse('notes:delete', args=(self.note_1.slug,))
        response = self.auth_client.delete(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверка пользователь author не может редактировать чужую запись!"""
        edit_url = reverse('notes:edit', args=(self.note_1.slug,))
        response = self.auth_client.get(edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
