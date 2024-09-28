# Применение встроенной фикстуры admin_client может дать побочный эффект,
# если вдруг права администратора системы будут более широкими, чем права
# обычного залогиненного пользователя. Поэтому лучше не «злоупотреблять»
# с фикстурой admin_client, а создать отдельную пользовательскую фикстуру
# для залогиненного пользователя.

# Для тестирования понадобятся фикстуры, которые возвращают:
# 1 - объекты двух пользователей — автора заметки и обычного пользователя,
# 2 - два клиента, авторизованных для обычного пользователя и автора,
# 3 - объект заметки.

import pytest

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from notes.models import Note


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


# Фикстура note создает обьект заметки. Можно вызвать из любого места.
@pytest.fixture
def note(author):
    note = Note.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def slug_for_args(note):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (note.slug,)


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }
