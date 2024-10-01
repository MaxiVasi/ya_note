# В файле test_logic.py:
# Залогиненный пользователь может создать заметку, а анонимный — не может. ++
# Невозможно создать две заметки с одинаковым slug.
# Если при создании заметки не заполнен slug, то он формируется автоматически, +
# с помощью функции pytils.translit.slugify.
# Пользователь может редактировать и удалять свои заметки, ++
# но не может редактировать или удалять чужие. ++

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
    NEW_TEXT = 'Новый текст заметки'
    SLUG = 'тестовое'
    ADD_URL = reverse('notes:add')

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
        cls.data = {'title': 'Новый', 'text': 'Текст'}
        cls.newtextdata = {'title': cls.TITLE, 'text': cls.NEW_TEXT}
        cls.author_1 = User.objects.create(username='user_author_1')
        cls.auth_client_1 = Client()
        cls.auth_client_1.force_login(cls.author_1)
        cls.note_1 = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author_1,
            slug=slugify(cls.TITLE) + '1',
        )

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать запись->"""
        self.client.post(self.ADD_URL, data=self.data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_author_can_create_note_and_slug_transformation(self):
        """Пользователь author может создать запись->"""
        response = self.auth_client.post(self.ADD_URL, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 3)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, 'Новый')
        self.assertEqual(new_note.text, 'Текст')
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.slug, slugify(new_note.title))

    def test_author_cant_edit_note_of_another_user(self):
        """Пользователь author не может редактировать чужую запись->"""
        edit_url = reverse('notes:edit', args=(self.note_1.slug,))
        response = self.auth_client.get(edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_cant_delete_note_of_another_user(self):
        """Пользователь author не может удалить запись author_1->"""
        delete_url = reverse('notes:delete', args=(self.note_1.slug,))
        response = self.auth_client.delete(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_author_can_edit_note(self):
        """Пользователь author может редактировать свою запись->"""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.post(edit_url, data=self.newtextdata)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_author_can_delete_note(self):
        """Пользователь author может удалить свою запись->"""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client.delete(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_creation_two_notes_with_one_slug(self):
        current_notes_count = Note.objects.count()
        current_slug = Note.objects.last().slug
        newdata = {'title': 'Новый', 'text': 'Текст', 'slug': current_slug}
        self.auth_client.post(self.ADD_URL, data=newdata)
        new_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, new_notes_count)
