from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'shopp.db'

#  ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ при запуске
def init_db():
    """Создает таблицу Products если её нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL CHECK(price > 0),
            stock_quantity INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print(" База данных shopp.db инициализирована")

# Вспомогательная функция подключения к БД
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # возвращает словари
    return conn

# Инициализация БД при старте приложения
with app.app_context():
    init_db()

# 1. CREATE (POST /api/products) - создать товар
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    #  ВАЛИДАЦИЯ на сервере (обязательно!)
    if not data or not data.get('name') or not data.get('price') or data.get('price') <= 0:
        return jsonify({'error': 'Название и цена (price > 0) обязательны'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Products (name, description, price, stock_quantity) VALUES (?, ?, ?, ?)",
            (data['name'], data.get('description'), data['price'], data.get('stock_quantity', 0))
        )
        product_id = cursor.lastrowid
        conn.commit()
        return jsonify({'id': product_id, 'message': 'Товар создан'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ошибка при создании товара'}), 400
    finally:
        conn.close()

# 2. READ (GET /api/products) - список товаров
@app.route('/api/products', methods=['GET'])
def list_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, stock_quantity FROM Products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

# 3. READ (GET /api/products/<id>) - один товар
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return jsonify({'error': 'Товар не найден'}), 404
    
    return jsonify(dict(product))

# 4. UPDATE (PUT /api/products/<id>) - обновить товар
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    #  ВАЛИДАЦИЯ
    if not data.get('name') or not data.get('price') or data['price'] <= 0:
        return jsonify({'error': 'Название и цена (price > 0) обязательны'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Products SET name = ?, description = ?, price = ?, stock_quantity = ?
            WHERE id = ?
        """, (data['name'], data.get('description'), data['price'], data.get('stock_quantity', 0), product_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Товар не найден'}), 404
        
        conn.commit()
        return jsonify({'message': 'Товар обновлен'})
    finally:
        conn.close()

# 5. DELETE (DELETE /api/products/<id>)
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Товар не найден'}), 404
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Товар удален'})

if __name__ == '__main__':
    print(" Flask CRUD API запущен на http://localhost:5000")
    print(" Тестируй через браузер или Postman:")
    print("GET    http://localhost:5000/api/products")
    print("POST   http://localhost:5000/api/products")
    print("GET    http://localhost:5000/api/products/1")
    print("PUT    http://localhost:5000/api/products/1")
    print("DELETE http://localhost:5000/api/products/1")
    
    #  ЯВНО указываем порт 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
