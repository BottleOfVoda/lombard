@echo off
echo Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo Установка необходимых пакетов...
pip install selenium pytest webdriver-manager pytest-xdist

echo Окружение настроено!
echo Запустите тесты командой: python -m pytest integration_tests/test_auth_and_booking.py -v 