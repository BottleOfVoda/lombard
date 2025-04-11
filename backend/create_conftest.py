# create_conftest.py - скрипт для создания conftest.py
with open('tests/conftest.py', 'w') as f:
    f.write('''import pytest
import sys
import os

# Добавляем корневую папку бэкенда в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Мок для функции get_db_connection, чтобы тесты не трогали реальную БД
@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    # Настраиваем курсор так, чтобы он работал с 'with' statement
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    # Также настроим для DictCursor, если он используется без 'with'
    mock_dict_cursor = mocker.MagicMock()
    mocker.patch('psycopg2.extras.DictCursor', return_value=mock_dict_cursor)

    # Мокаем саму функцию подключения
    mocker.patch('app.get_db_connection', return_value=mock_conn)
    # Возвращаем моки, чтобы их можно было использовать в тестах
    return {'conn': mock_conn, 'cursor': mock_cursor, 'dict_cursor': mock_dict_cursor}
''') 