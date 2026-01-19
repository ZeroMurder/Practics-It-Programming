from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import re
import hashlib
import os

app = Flask(__name__)
DB_PATH = 'shop.db'

def init_db():
    """ Пересоздаёт БД с правильной структурой"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  Старая БД удалена")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(" БД создана")

def get_users():
    """Получает всех пользователей"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, email, name, created_at FROM users ORDER BY id DESC")
    users = [{"id": r[0], "email": r[1], "name": r[2], "created": r[3]} for r in c.fetchall()]
    conn.close()
    return users

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    profile = ''
    users = get_users()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'register':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            name = request.form.get('name', '').strip()
            
            print(f"🔍 Регистрация: {email}")
            
            #  ВАЛИДАЦИЯ
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                message = ' Неверный email'
            elif len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
                message = ' Пароль: 8+ символов, заглавная буква, цифра'
            elif len(name) < 2 or not all(c.isalpha() or c.isspace() for c in name):
                message = ' Имя: только буквы, минимум 2 символа'
            else:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("SELECT id FROM users WHERE email = ?", (email,))
                    if c.fetchone():
                        message = ' Email уже зарегистрирован'
                    else:
                        hash_pw = hashlib.sha256(password.encode()).hexdigest()
                        c.execute("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)", 
                                 (email, hash_pw, name))
                        conn.commit()
                        user_id = c.lastrowid
                        conn.close()
                        
                        profile = f'''
                        <div style="background: linear-gradient(135deg, #28a745, #20c997); 
                                    color: white; padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center;">
                            <h3>🎉 Регистрация УСПЕШНА!</h3>
                            <p><strong>ID:</strong> {user_id}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Имя:</strong> {name}</p>
                        </div>'''
                        message = f' Пользователь <strong>{name}</strong> создан!'
                        users = get_users()  # Обновляем список
                        
                except Exception as e:
                    message = f' Ошибка: {str(e)}'
    
    users_html = ''
    if users:
        users_html = '''
        <div style="background: #e7f3ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3> Все пользователи ({len(users)})</h3>
            <div style="max-height: 300px; overflow-y: auto;">
        '''
        for user in users:
            users_html += f'''
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; background: white;">
                    <strong>ID:</strong> {user['id']} | 
                    <strong>{user['name']}</strong> 
                    <br><small>Email: {user['email']} | Создан: {user['created'][:19]}</small>
                </div>
            '''
        users_html += '</div></div>'
    else:
        users_html = '<div style="text-align: center; color: #666; margin: 20px 0;">📭 Пользователей пока нет</div>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title> Регистрация + Список пользователей</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; background: #f0f2f5; }}
        .form {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
        h2 {{ text-align: center; color: #333; margin-bottom: 30px; }}
        input {{ 
            width: 100%; padding: 15px; margin: 10px 0; 
            border: 2px solid #ddd; border-radius: 10px; 
            font-size: 16px; box-sizing: border-box;
        }}
        input:focus {{ border-color: #28a745; outline: none; box-shadow: 0 0 0 3px rgba(40,167,69,0.1); }}
        button {{ 
            width: 100%; padding: 18px; background: #28a745; 
            color: white; border: none; border-radius: 10px; 
            font-size: 18px; font-weight: bold; cursor: pointer; margin: 10px 0;
        }}
        button:hover {{ background: #218838; transform: translateY(-2px); }}
        .error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #dc3545; }}
        .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #28a745; }}
        .users-section {{ background: #e7f3ff; padding: 25px; border-radius: 15px; margin: 20px 0; }}
        .test-btn {{ background: #007bff; margin: 8px 0; font-size: 16px; }}
        .test-btn:hover {{ background: #0056b3; }}
        .user-card {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; background: white; transition: box-shadow 0.3s; }}
        .user-card:hover {{ box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="form">
        <h2> Форма регистрации</h2>
        
        <form method="POST">
            <input type="hidden" name="action" value="register">
            <input type="email" name="email" placeholder="test@example.com" value="{request.form.get('email', '') if request.method == 'POST' else ''}" required>
            <input type="password" name="password" placeholder="Pass1234 (8+ символов)" required>
            <input type="text" name="name" placeholder="Имя Фамилия" value="{request.form.get('name', '') if request.method == 'POST' else ''}" required>
            <button type="submit"> Зарегистрироваться</button>
        </form>
        
        {profile or ''}
        {message and f'<div class="{"success" if "✅" in message else "error"}">{message}</div>' or ''}
        
        {users_html}
        
        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 10px; font-size: 14px; text-align: center;">
            <strong> Всего пользователей: {len(users)}</strong>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>🧪 Быстрые тесты:</h3>
            <form method="POST" style="margin: 10px 0;">
                <input type="hidden" name="action" value="register">
                <input type="hidden" name="email" value="test{len(users)+1}@test.ru">
                <input type="hidden" name="password" value="Pass1234">
                <input type="hidden" name="name" value="Тест Пользователь {len(users)+1}">
                <button class="test-btn" type="submit"> Добавить тестового</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    print(" Сервер: http://localhost:5002")
    print(" Регистрация + список пользователей!")
    app.run(debug=True, port=5002)
