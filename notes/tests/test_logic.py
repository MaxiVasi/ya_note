# В файле test_logic.py:
# Залогиненный пользователь может создать заметку, а анонимный — не может. ++
# Невозможно создать две заметки с одинаковым slug.
# Если при создании заметки не заполнен slug, то он формируется автоматически, +
# с помощью функции pytils.translit.slugify.
# Пользователь может редактировать и удалять свои заметки, ++
# но не может редактировать или удалять чужие. ++

from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.tests.fixture import BaseTestFixture
from notes.forms import WARNING
from notes.models import Note


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
        edit_url = reverse(self.EDITS_URL, args=(self.note_1.slug,))
        response = self.author_client.post(edit_url, data=self.newtextdata)
        note_after = Note.objects.get(slug=self.note_1.slug)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note_1.title, note_after.title)
        self.assertEqual(self.note_1.text, note_after.text)
        self.assertEqual(self.note_1.author, note_after.author)
        self.assertEqual(self.note_1.slug, slugify(self.TITLE) + '1')

    def test_author_cant_delete_note_of_another_user(self):
        """Пользователь author не может удалить запись author_1->"""
        notes_count_before = Note.objects.count()
        delete_url = reverse(self.DELETES_URL, args=(self.note_1.slug,))
        response = self.author_client.delete(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(notes_count_before, note_count)

    def test_author_can_edit_note(self):
        """Пользователь author может редактировать свою запись->"""
        edit_url = reverse(self.EDITS_URL, args=(self.note.slug,))
        response = self.author_client.post(edit_url, data=self.newtextdata)
        self.assertRedirects(response, self.SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.newtextdata['title'])
        self.assertEqual(note.text, self.newtextdata['text'])
        self.assertEqual(note.author, self.newtextdata['author'])

    def test_author_can_delete_note(self):
        """Пользователь author может удалить свою запись->"""
        notes_count_before = Note.objects.count()
        delete_url = reverse(self.DELETES_URL, args=(self.note.slug,))
        response = self.author_client.delete(delete_url)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertEqual(notes_count_before, note_count + 1)

    def test_creation_two_notes_with_one_slug(self):
        """Невозможно создать две заметки с одинаковым slug->"""
        notes_count_before = Note.objects.count()
        current_slug = Note.objects.last().slug
        newdata = {'title': 'Новый', 'text': 'Текст', 'slug': current_slug}
        self.author_client.post(self.ADD_URL, data=newdata)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count)
        response = self.author_client.post(self.ADD_URL, data=newdata)
        self.assertFormError(
            response, 'form', 'slug', errors=(newdata['slug'] + WARNING))
