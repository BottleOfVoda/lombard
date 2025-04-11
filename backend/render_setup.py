#!/usr/bin/env python
"""
Скрипт для проверки и настройки подключения к базе данных при деплое на Render.
Запускается автоматически при buildCommand в render.yaml
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
import time

# Загружаем переменные среды
load_dotenv()

# Получаем параметры подключения из переменных среды
DB_NAME = os.getenv("DB_NAME", "Lombard")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_db_connection():
    """Проверяет подключение к базе данных"""
    print("Проверка подключения к базе данных...")
    
    # Проверяем наличие необходимых параметров
    if not all([DB_HOST, DB_PASSWORD]):
        print("ОШИБКА: Отсутствуют необходимые параметры подключения к БД")
        print("Убедитесь, что заданы переменные среды DB_HOST и DB_PASSWORD")
        return False
    
    try:
        # Пытаемся подключиться к БД
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Проверяем подключение
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Успешное подключение к PostgreSQL: {version[0]}")
        
        # Проверяем наличие таблиц
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()
        print(f"Найдено таблиц в БД: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"ОШИБКА подключения к БД: {e}")
        return False

def main():
    """Основная функция для проверки и настройки перед деплоем"""
    print("Запуск скрипта подготовки к деплою на Render...")
    
    # Проверяем подключение к БД с повторными попытками
    max_retries = 3
    retry_delay = 5  # секунд
    
    for i in range(max_retries):
        if check_db_connection():
            print("Подготовка к деплою успешно завершена!")
            return 0
        else:
            if i < max_retries - 1:
                print(f"Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
    
    print("Не удалось подключиться к базе данных после нескольких попыток.")
    print("Проверьте настройки подключения и доступность БД.")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 