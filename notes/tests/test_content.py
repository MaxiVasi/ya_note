# В файле test_content.py:
# Отдельная заметка передаётся на страницу со списком заметок в списке object_list в словаре context;
# В список заметок одного пользователя не попадают заметки другого пользователя;
# На страницы создания и редактирования заметки передаются формы.

from django.urls import reverse

from notes.tests.fixture import BaseTestFixture
from notes.forms import NoteForm


class TestContent(BaseTestFixture):

    def test_notes_creation_by_author(self):
        """Проверка что запись автора есть на старнице записей автора->"""
        response = self.author_client.get(self.LIST_URL)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_in_list_from_another_author(self):
        """Проверка что запись автора_1 нет на старнице записей автора->"""
        response = self.author_client.get(self.LIST_URL)
        self.assertNotIn(self.note_1, response.context['object_list'])

    def test_authorized_client_has_form_on_edit_page(self):
        """Проверяем что на странице редактирования заметки есть форма->"""
        edit_urls = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.get(edit_urls)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_on_add_page(self):
        """Проверяем что на странице добавления заметки есть форма->"""
        response = self.author_client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
