import sqlite3
import os
from datetime import datetime

print("🛒 ИСПРАВЛЕННАЯ БД интернет-магазина")
print(f"Работаем в: {os.getcwd()}")

#  Фикс: абсолютный путь + обработка ошибок
db_path = os.path.join(os.getcwd(), 'shop.db')
print(f"Создаем БД: {db_path}")

try:
    # Подключение с проверкой
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # Включаем внешние ключи
    cursor = conn.cursor()
    
    print(" Создаем таблицы...")
    
    # Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL CHECK (price > 0),
        stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0)
    )
    ''')
    
    # Orders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        total_amount REAL NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    )
    ''')
    
    # OrderItems
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_at_order REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders(id),
        FOREIGN KEY (product_id) REFERENCES Products(id)
    )
    ''')
    
    # Данные (с обработкой UNIQUE)
    print(" Заполняем данными...")
    cursor.execute("INSERT OR IGNORE INTO Users VALUES (1, 'user@test.ru', 'hash123', 'Иван Иванов', CURRENT_TIMESTAMP)")
    cursor.execute("INSERT OR IGNORE INTO Products VALUES (1, 'iPhone 15', 'Смартфон', 50000.0, 10)")
    cursor.execute("INSERT OR IGNORE INTO Products VALUES (2, 'Футболка', 'Хлопок', 1000.0, 50)")
    cursor.execute("INSERT OR IGNORE INTO Orders VALUES (1, 1, 'paid', 51000.0, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT OR IGNORE INTO OrderItems VALUES (1, 1, 1, 1, 50000.0)")
    cursor.execute("INSERT OR IGNORE INTO OrderItems VALUES (2, 1, 2, 10, 1000.0)")
    
    conn.commit()
    
    # ✅ ГЛАВНЫЙ ЗАПРОС
    print("\n ВЫПОЛНЯЕМ ЗАПРОС ИЗ ЗАДАНИЯ:")
    cursor.execute('''
    SELECT 
        o.id AS order_id,
        o.order_date,
        o.status,
        COUNT(oi.id) AS items_count,
        SUM(oi.quantity * oi.price_at_order) AS total_sum
    FROM Orders o
    LEFT JOIN OrderItems oi ON o.id = oi.order_id
    WHERE o.user_id = 1
    GROUP BY o.id
    ORDER BY o.order_date DESC
    ''')
    
    results = cursor.fetchall()
    print("РЕЗУЛЬТАТ:")
    for row in results:
        print(f"  Заказ #{row[0]} | {row[1]} | {row[2].upper()} | {row[3]} товаров | {row[4]:,.0f}₽")
    
    # Проверка файла
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"\n✅ ФАЙЛ СОЗДАН: {db_path} ({size} байт)")
    else:
        print(" Файл НЕ создан!")
    
except Exception as e:
    print(f" ОШИБКА: {e}")
    
finally:
    conn.close()
    print("\n Задание 1 Пройдено!")
