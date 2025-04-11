# backend/hash_passwords.py
import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

# Загружаем переменные окружения (данные для подключения к БД)
load_dotenv()

# --- Настройки ---
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
TABLE_NAME = "users"  # УКАЖИ ПРАВИЛЬНОЕ ИМЯ ТВОЕЙ ТАБЛИЦЫ!
PLAIN_COLUMN = "password_plain" # Имя временного столбца с паролями
HASH_COLUMN = "password_hash"   # Имя нового столбца для хэшей
ID_COLUMN = "id"                # Имя столбца с ID пользователя
LOGIN_COLUMN = "username"        # Имя столбца с логином (для логов)

def hash_existing_passwords():
    conn = None
    cur = None
    updated_count = 0
    error_count = 0

    if not all([DB_NAME, DB_USER, DB_PASSWORD]):
        print("Ошибка: Не все переменные окружения для БД (DB_NAME, DB_USER, DB_PASSWORD) заданы в файле .env")
        return

    try:
        print(f"Подключение к базе данных '{DB_NAME}' на '{DB_HOST}:{DB_PORT}'...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Подключение успешно.")
        cur = conn.cursor()

        # Выбираем пользователей, у которых еще нет хэша (или есть пароль в старом поле)
        # Выбираем id, login и пароль в открытом виде
        select_query = f"""
            SELECT {ID_COLUMN}, {LOGIN_COLUMN}, {PLAIN_COLUMN}
            FROM {TABLE_NAME}
            WHERE {PLAIN_COLUMN} IS NOT NULL AND ({HASH_COLUMN} IS NULL OR {HASH_COLUMN} = '')
        """
        print(f"Выполняем запрос: {select_query}")
        cur.execute(select_query)
        users_to_update = cur.fetchall()

        if not users_to_update:
            print("Не найдено пользователей для обновления паролей.")
            return

        print(f"Найдено {len(users_to_update)} пользователей для хэширования паролей...")

        for user_id, login, plain_password in users_to_update:
            try:
                if not plain_password: # Пропускаем пустые пароли, если такие есть
                    print(f"  - Пропущен пользователь ID={user_id}, login='{login}' (пустой пароль)")
                    continue

                print(f"  - Хэшируем пароль для пользователя ID={user_id}, login='{login}'...")
                # Хэшируем пароль
                hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
                hashed_password_str = hashed_password.decode('utf-8')

                # Обновляем запись в БД
                update_query = f"""
                    UPDATE {TABLE_NAME}
                    SET {HASH_COLUMN} = %s
                    WHERE {ID_COLUMN} = %s
                """
                cur.execute(update_query, (hashed_password_str, user_id))
                print(f"    -> Успешно обновлен хэш для ID={user_id}")
                updated_count += 1

            except Exception as e:
                print(f"    -> ОШИБКА при обработке пользователя ID={user_id}, login='{login}': {e}")
                error_count += 1
                conn.rollback() # Откатываем последнее обновление при ошибке
                # Можно добавить continue, чтобы не пытаться коммитить после ошибки

        # Фиксируем все успешные изменения
        if updated_count > 0:
             print("Сохранение изменений в базе данных...")
             conn.commit()
             print("Изменения сохранены.")
        else:
             print("Нет изменений для сохранения.")


    except psycopg2.Error as e:
        print(f"Ошибка базы данных: {e}")
        if conn:
            conn.rollback() # Откатываем транзакцию при ошибке подключения или выполнения запроса
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("Соединение с базой данных закрыто.")

    print("\n--- Итоги ---")
    print(f"Успешно обновлено паролей: {updated_count}")
    print(f"Ошибок при обработке: {error_count}")

if __name__ == "__main__":
    hash_existing_passwords()