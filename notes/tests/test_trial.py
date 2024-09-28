from django.test import Client, TestCase

from notes.models import Note
from django.contrib.auth import get_user_model

from pytils.translit import slugify

User = get_user_model()


class TestNotes(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Тестовый текст записи'
    SLUG = 'тестовое'

    @classmethod
    def setUpTestData(cls):
        """Наполняем фикстурами нашу базу."""
        # проверка возможности создания записи зарегистрированным пользователем.
        cls.user = User.objects.create(username='testUser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=slugify(cls.SLUG),
            author=cls.user,
        )

    def test_slug(self):
        # Проверяем транслитерацию поля slug.
        self.assertEqual(self.note.slug, 'testovoe')

    def test_successful_creation(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_title(self):
        self.assertEqual(self.note.title, 'Заголовок')
