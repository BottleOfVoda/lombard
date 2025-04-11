from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import psycopg2
import bcrypt
import os
from dotenv import load_dotenv
from psycopg2 import errors # Импортируем ошибки psycopg2 для обработки UniqueViolation
from psycopg2.extras import DictCursor
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Загружаем переменные окружения из файла .env
load_dotenv()

app = Flask(__name__)
# Настраиваем CORS (Упрощенная версия для отладки)
CORS(app)
# --- Настройки подключения к БД (лучше через переменные окружения) ---
DB_NAME = os.getenv("DB_NAME", "Lombard")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") # Добавляем загрузку пароля из .env
DB_HOST = os.getenv("DB_HOST", "localhost") # или другой хост
DB_PORT = os.getenv("DB_PORT", "5432")     # или другой порт

def get_db_connection():
    """Устанавливает соединение с базой данных PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        # В реальном приложении здесь лучше логировать ошибку
        return None

# --- Эндпоинты API ---
# Добавьте в конец файла или перед другими маршрутами:

@app.route('/')
def index():
    return jsonify({
        "message": "Ломбард Авангард API",
        "status": "running", 
        "endpoints": [
            "/api/login", 
            "/api/register", 
            "/api/products"
        ]
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Получаем новые поля
    full_name = data.get('fullName') # Имена в camelCase от фронтенда
    phone_number = data.get('phoneNumber')
    email = data.get('email')

    # --- Базовая валидация --- 
    if not username or not password:
        return jsonify({"message": "Требуется логин и пароль"}), 400
    # Можно добавить проверку email, если он обязателен
    if not email:
         return jsonify({"message": "Требуется Email"}), 400
    # TODO: Более строгая валидация email, телефона и т.д. по желанию
    # ------------------------

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor() as cur:
            # 1. Проверить, не занят ли username (оставляем)
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return jsonify({"message": "Пользователь с таким логином уже существует"}), 409

            # 2. Хэшировать пароль (оставляем)
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')

            # 3. Сохранить нового пользователя в БД (с новыми полями)
            sql_insert = """
                INSERT INTO users (username, password_hash, role, full_name, phone_number, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql_insert, (
                username, 
                hashed_password_str, 
                'user', # Роль по умолчанию
                full_name, 
                phone_number, 
                email
            ))
            conn.commit() 

            return jsonify({"message": "Пользователь успешно зарегистрирован"}), 201

    except errors.UniqueViolation as e: # Обрабатываем ошибку уникальности (для email или username)
        if conn:
            conn.rollback()
        # Проверяем, на какое поле сработал unique constraint
        # Это не самый надежный способ, зависит от сообщения об ошибке БД
        error_detail = str(e).lower()
        if 'email' in error_detail:
             return jsonify({"message": "Пользователь с таким email уже существует"}), 409
        elif 'username' in error_detail: # На случай, если проверка fetchone() не сработала
            return jsonify({"message": "Пользователь с таким логином уже существует"}), 409
        else:
            print(f"Ошибка уникальности при регистрации: {e}")
            return jsonify({"message": "Ошибка уникальности данных при регистрации"}), 409

    except psycopg2.Error as e: # Обработка других ошибок БД
        if conn:
            conn.rollback()
        print(f"Ошибка при регистрации: {e}")
        return jsonify({"message": "Ошибка на сервере при регистрации"}), 500
    except Exception as e: # Обработка прочих ошибок
        print(f"Неожиданная ошибка при регистрации: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Требуется логин и пароль"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Ищем пользователя по имени пользователя и получаем ID, хэш пароля (password_hash) и РОЛЬ
        cursor.execute("SELECT id, password_hash, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        # conn.close() # Закрывать соединение здесь преждевременно, если проверка пароля не удалась
        
        # Проверяем, найден ли пользователь и совпадает ли пароль
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            conn.close() # Закрываем соединение после успешной проверки
            # Пароль верный, возвращаем ID пользователя и его РОЛЬ
            return jsonify({'message': 'Login successful', 'user_id': user['id'], 'role': user['role']}), 200
        else:
            if conn:
                conn.close() # Закрываем соединение, если пользователь не найден или пароль неверный
            # Неверные учетные данные
            return jsonify({"message": "Неверный логин или пароль"}), 401 # 401 Unauthorized

    except psycopg2.Error as e:
        print(f"Ошибка при входе: {e}")
        return jsonify({"message": "Ошибка на сервере при входе"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при входе: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500

# --- Новый эндпоинт для получения списка товаров ---
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor() as cur:
            # Выбираем нужные поля из таблицы products
            cur.execute("SELECT id, name, price, is_booked, image_url FROM products ORDER BY id") # Добавим сортировку по ID
            products_raw = cur.fetchall()

            # Преобразуем результат (список кортежей) в список словарей
            products_list = []
            if products_raw:
                # Получаем имена колонок из описания курсора
                colnames = [desc[0] for desc in cur.description]
                for row in products_raw:
                    product_dict = dict(zip(colnames, row))
                    # Преобразуем Decimal в строку или float для JSON-сериализации
                    if 'price' in product_dict and product_dict['price'] is not None:
                         product_dict['price'] = float(product_dict['price']) # или str()
                    products_list.append(product_dict)

            return jsonify(products_list), 200

    except psycopg2.Error as e:
        print(f"Ошибка при получении списка товаров: {e}")
        return jsonify({"message": "Ошибка на сервере при получении товаров"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при получении списка товаров: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

# --- Новый эндпоинт для добавления товара ---
@app.route('/api/products', methods=['POST'])
def add_product():
    conn = None
    try:
        # Получаем данные из JSON тела запроса
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        image_url = data.get('image_url') # Может быть пустым

        # Простая валидация
        if not name or price is None:
            return jsonify({"message": "Необходимо указать название и цену товара"}), 400

        # Проверка, что цена является числом
        try:
            price = float(price) # Попробуем преобразовать в число
            if price < 0:
                 return jsonify({"message": "Цена не может быть отрицательной"}), 400
        except ValueError:
            return jsonify({"message": "Цена должна быть числом"}), 400

        # Подключение к БД
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Вставляем новый товар
        # is_booked по умолчанию FALSE (если не указано иное в схеме БД)
        cursor.execute(
            "INSERT INTO products (name, price, image_url) VALUES (%s, %s, %s) RETURNING id",
            (name, price, image_url or None) # Используем None, если image_url пустой
        )
        new_product_id = cursor.fetchone()['id']
        
        conn.commit() # Фиксируем изменения
        cursor.close()
        
        return jsonify({"message": "Товар успешно добавлен", "product_id": new_product_id}), 201 # 201 Created

    except psycopg2.Error as e:
        print(f"Ошибка базы данных при добавлении товара: {e}")
        if conn:
            conn.rollback() # Откатываем изменения в случае ошибки БД
        return jsonify({"message": "Ошибка базы данных при добавлении товара"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при добавлении товара: {e}")
        if conn:
            conn.rollback()
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

# --- Новый эндпоинт для бронирования товара ---
@app.route('/api/products/<int:product_id>/book', methods=['PUT'])
def book_product(product_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor() as cur:
            # Проверяем, существует ли товар и не забронирован ли он уже
            cur.execute("SELECT is_booked FROM products WHERE id = %s", (product_id,))
            product_status = cur.fetchone()

            if product_status is None:
                return jsonify({"message": "Товар не найден"}), 404 # Not Found
            
            if product_status[0] is True: # Если is_booked уже True
                return jsonify({"message": "Товар уже забронирован"}), 409 # Conflict

            # Обновляем статус is_booked на TRUE
            cur.execute("UPDATE products SET is_booked = TRUE WHERE id = %s", (product_id,))
            conn.commit() # Подтверждаем транзакцию
            
            # Возвращаем сообщение об успехе
            return jsonify({"message": f"Товар {product_id} успешно забронирован"}), 200

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Ошибка при бронировании товара {product_id}: {e}")
        return jsonify({"message": "Ошибка на сервере при бронировании"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при бронировании товара {product_id}: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

# --- Новый эндпоинт для СНЯТИЯ брони товара ---
@app.route('/api/products/<int:product_id>/unbook', methods=['PUT'])
def unbook_product(product_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor() as cur:
            # Проверяем, существует ли товар и забронирован ли он
            cur.execute("SELECT is_booked FROM products WHERE id = %s", (product_id,))
            product_status = cur.fetchone()

            if product_status is None:
                return jsonify({"message": "Товар не найден"}), 404 # Not Found
            
            if product_status[0] is False: # Если is_booked уже False
                return jsonify({"message": "Товар не был забронирован"}), 409 # Conflict

            # Обновляем статус is_booked на FALSE
            cur.execute("UPDATE products SET is_booked = FALSE WHERE id = %s", (product_id,))
            conn.commit() # Подтверждаем транзакцию
            
            # Возвращаем сообщение об успехе
            return jsonify({"message": f"Бронь с товара {product_id} снята"}), 200

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Ошибка при снятии брони с товара {product_id}: {e}")
        return jsonify({"message": "Ошибка на сервере при снятии брони"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при снятии брони с товара {product_id}: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

# --- Новый эндпоинт для получения данных пользователя по ID ---
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_data(user_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor() as cur:
            # Выбираем нужные поля из таблицы users по ID
            cur.execute("SELECT username, full_name, phone_number, email FROM users WHERE id = %s", (user_id,))
            user_raw = cur.fetchone()

            if user_raw is None:
                return jsonify({"message": "Пользователь не найден"}), 404

            # Преобразуем результат в словарь
            colnames = [desc[0] for desc in cur.description]
            user_data = dict(zip(colnames, user_raw))
            
            # Возвращаем данные пользователя (пароль и роль не возвращаем)
            return jsonify(user_data), 200

    except psycopg2.Error as e:
        print(f"Ошибка при получении данных пользователя {user_id}: {e}")
        return jsonify({"message": "Ошибка на сервере при получении данных пользователя"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при получении данных пользователя {user_id}: {e}")
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500
    finally:
        if conn:
            conn.close()

# --- Эндпоинт для удаления товара (только для админов) ---
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = None
    try:
        # TODO: В реальном приложении здесь нужна проверка прав администратора!
        # Например, получить токен из заголовка Authorization, проверить пользователя и его роль.
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500
        
        with conn.cursor() as cur:
            # Проверяем, существует ли товар перед удалением (опционально, но хорошо)
            cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
            product_exists = cur.fetchone()
            
            if not product_exists:
                conn.close()
                return jsonify({"message": "Товар не найден"}), 404

            # Удаляем товар
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit() # Фиксируем удаление
        
        conn.close()
        return jsonify({"message": "Товар успешно удален"}), 200 # или 204 No Content

    except psycopg2.Error as e:
        print(f"Ошибка базы данных при удалении товара {product_id}: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"message": "Ошибка базы данных при удалении товара"}), 500
    except Exception as e:
        print(f"Неожиданная ошибка при удалении товара {product_id}: {e}")
        if conn:
            conn.close()
        return jsonify({"message": "Неожиданная ошибка на сервере"}), 500

# --- Эндпоинт для генерации PDF с забронированными товарами ---
@app.route('/api/generate-booked-pdf', methods=['GET'])
def generate_booked_pdf():
    conn = None
    # --- Регистрация шрифта DejaVu --- 
    registered_font_name = 'Helvetica' # Имя шрифта по умолчанию
    try:
        # Указываем имя 'DejaVu' и путь к файлу 'DejaVuSans.ttf'
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        registered_font_name = 'DejaVu' # Если успешно, будем использовать это имя
        print("Successfully registered font DejaVuSans.ttf")
    except Exception as e:
        print(f"WARNING: Could not register font DejaVuSans.ttf. Cyrillic text might render incorrectly. Error: {e}")
        print("Ensure DejaVuSans.ttf is in the same directory as app.py or provide the full path.")
        # Продолжаем с шрифтом по умолчанию 'Helvetica'

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Ошибка подключения к базе данных"}), 500

        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Выбираем только забронированные товары
            cur.execute("SELECT id, name, price FROM products WHERE is_booked = TRUE ORDER BY name")
            booked_items = cur.fetchall()

        if not booked_items:
            # Если нет забронированных товаров, можно вернуть ошибку или пустой PDF?
            # Вернем ошибку, что нет данных для отчета
             return jsonify({"message": "Нет забронированных товаров для генерации отчета"}), 404

        # --- Генерация PDF --- 
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        title_style = None 

        # Устанавливаем зарегистрированный шрифт для стилей
        # (Этот try/except блок больше не нужен, так как мы уже обработали ошибку регистрации)
        styles['Normal'].fontName = registered_font_name
        print(f"Using font: {registered_font_name} for Normal style")

        # Создаем кастомный стиль для заголовка на основе Normal
        title_style = ParagraphStyle(
            name='PdfTitle',
            parent=styles['Normal'], # Наследует шрифт от Normal
            fontSize=16,
            alignment=1,
            spaceAfter=14
            # bold=0, italic=0 - уже не нужны, если шрифт обычный
        )

        # Проверка на случай, если что-то пошло не так с созданием стиля
        if not title_style:
             title_style = styles['h1'] 
             title_style.fontName = registered_font_name
             title_style.alignment = 1 
             print("WARNING: Failed to create custom title style, falling back to modified h1.")

        story = []

        # Заголовок (использует title_style с нужным шрифтом)
        title = "Список забронированных товаров"
        story.append(Paragraph(title, title_style)) 

        # Данные для таблицы (без ID)
        data = [['Название', 'Цена (руб.)']] # Убираем 'ID' из заголовков
        for item in booked_items:
             price_str = str(item['price']) if item['price'] is not None else 'N/A'
             data.append([
                 # Paragraph(str(item['id']), styles['Normal']), # Убираем ID
                 Paragraph(item['name'], styles['Normal']),
                 Paragraph(price_str, styles['Normal']) 
             ])

        # Создание таблицы (корректируем colWidths)
        table = Table(data, colWidths=[4.5*inch, 1.5*inch]) # Убираем ширину для ID

        # Стили таблицы (корректируем диапазоны, если необходимо)
        # Так как диапазоны используют относительные индексы (-1), 
        # большинство стилей должны работать без изменений.
        # Нужно проверить стиль для первой колонки, если он был специфичен.
        # Стили ниже должны быть ОК.
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), registered_font_name), 
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(style)

        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Дата генерации отчета (использует styles['Normal'])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Отчет сгенерирован: {now}", styles['Normal']))

        # Сборка документа
        doc.build(story)
        # --- Конец генерации PDF ---

        buffer.seek(0)
        
        # Генерация имени файла с датой и временем
        filename = f"booked_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Отправка файла пользователю
        return send_file(
            buffer, 
            mimetype='application/pdf',
            as_attachment=True, # Скачать как вложение
            download_name=filename # Имя файла для скачивания
        )

    except psycopg2.Error as e:
        print(f"Ошибка базы данных при генерации PDF: {e}")
        return jsonify({"message": "Ошибка базы данных при генерации отчета"}), 500
    except Exception as e:
        # Ловим ошибки генерации PDF или другие
        print(f"Ошибка при генерации PDF: {e}")
        return jsonify({"message": "Не удалось сгенерировать PDF отчет"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Запуск Flask development server
    # debug=True автоматически перезапускает сервер при изменениях кода
    # host='0.0.0.0' делает сервер доступным извне (не только с localhost)
    # port=5000 стандартный порт Flask
    app.run(debug=True, host='0.0.0.0', port=5000) 