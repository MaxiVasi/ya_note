# В файле test_logic.py:
# Залогиненный пользователь может создать заметку, а анонимный — не может. ++
# Невозможно создать две заметки с одинаковым slug.
# Если при создании заметки не заполнен slug, то он формируется автоматически, +
# с помощью функции pytils.translit.slugify.
# Пользователь может редактировать и удалять свои заметки, ++
# но не может редактировать или удалять чужие. ++

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from .fixture import BaseTestFixture
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesCreation(BaseTestFixture):

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать запись->"""
        notes_count_before = Note.objects.count()
        self.client.post(self.ADD_URL, data=self.data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count)

    def test_author_can_create_note_and_slug_transformation(self):
        """Пользователь author может создать запись->"""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.data)
        self.assertRedirects(response, self.SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count - 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.data['title'])
        self.assertEqual(new_note.text, self.data['text'])
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.slug, slugify(new_note.title))

    def test_author_cant_edit_note_of_another_user(self):
        """Пользователь author не может редактировать чужую запись->"""
        edit_url = reverse('notes:edit', args=(self.note_1.slug,))
        response = self.author_client.get(edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_cant_delete_note_of_another_user(self):
        """Пользователь author не может удалить запись author_1->"""
        notes_count_before = Note.objects.count()
        delete_url = reverse('notes:delete', args=(self.note_1.slug,))
        response = self.author_client.delete(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(notes_count_before, note_count)

    def test_author_can_edit_note(self):
        """Пользователь author может редактировать свою запись->"""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(edit_url, data=self.newtextdata)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_author_can_delete_note(self):
        """Пользователь author может удалить свою запись->"""
        notes_count_before = Note.objects.count()
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.delete(delete_url)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertEqual(notes_count_before, note_count + 1)

    def test_creation_two_notes_with_one_slug(self):
        notes_count_before = Note.objects.count()
        current_slug = Note.objects.last().slug
        newdata = {'title': 'Новый', 'text': 'Текст', 'slug': current_slug}
        self.author_client.post(self.ADD_URL, data=newdata)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count)
