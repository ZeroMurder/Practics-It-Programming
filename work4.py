from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'hotels.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  БД удалена")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        price INTEGER NOT NULL,
        stars INTEGER,
        available_rooms INTEGER DEFAULT 0,
        description TEXT
    )''')
    
    # 20+ тестовых отелей
    hotels_data = [
        ("Hilton Moscow Lena", "Москва", 6500, 5, 12, "5★ в центре Москвы"),
        ("Izmailovo Gamma", "Москва", 3200, 3, 25, "Удобное расположение"),
        ("Radisson Collection", "Москва", 8500, 5, 8, "Люкс в центре"),
        ("Novotel Sheremetyevo", "Москва", 4500, 4, 18, "Рядом с аэропортом"),
        ("Cosmopolitan Moscow", "Москва", 7200, 5, 10, "Современный дизайн"),
        ("Astoria", "СПб", 9200, 5, 6, "Исторический отель СПб"),
        ("Holiday Inn СПб", "СПб", 3800, 4, 15, "Комфортный отдых"),
        ("Park Inn Pribaltiyskaya", "СПб", 4100, 4, 22, "Вид на залив"),
        ("Courtyard by Marriott", "СПб", 5200, 4, 14, "Бизнес-класс"),
        ("Сочи Marriott Krasnaya Polyana", "Сочи", 11800, 5, 9, "Горнолыжный курорт"),
        ("Hyatt Regency Sochi", "Сочи", 9800, 5, 11, "Курортный комплекс"),
        ("Ibis Styles Sochi", "Сочи", 3900, 3, 30, "Бюджетный вариант"),
        ("Казань Hilton", "Казань", 6800, 5, 7, "Рядом с Кремлём"),
        ("Novotel Kazan Centre", "Казань", 4600, 4, 20, "Центр города"),
        ("Екатеринбург Hyatt", "Екатеринбург", 5900, 4, 16, "Бизнес-центр")
    ]
    
    c.executemany("INSERT INTO hotels(name, city, price, stars, available_rooms, description) VALUES (?, ?, ?, ?, ?, ?)", hotels_data)
    conn.commit()
    conn.close()
    print(" 15 отелей загружено!")

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title> Hotel Aggregator</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
            text-align: center; color: white; 
            font-size: 3rem; margin-bottom: 30px; 
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .filters { 
            background: white; padding: 30px; 
            border-radius: 20px; margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .filter-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        input, select, button { 
            padding: 15px; font-size: 16px; 
            border: 2px solid #e1e5e9; border-radius: 12px;
            transition: all 0.3s;
        }
        input:focus, select:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        button { 
            background: linear-gradient(135deg, #28a745, #20c997); 
            color: white; border: none; font-weight: bold; cursor: pointer;
            text-transform: uppercase; letter-spacing: 1px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(40,167,69,0.4); }
        .results { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; }
        .hotel-card { 
            background: white; padding: 25px; border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.4s;
        }
        .hotel-card:hover { 
            transform: translateY(-10px); box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }
        .hotel-name { font-size: 1.4rem; font-weight: bold; color: #333; margin-bottom: 10px; }
        .stars { color: #ffc107; font-size: 1.2rem; }
        .price { 
            font-size: 2rem; color: #28a745; font-weight: bold; 
            margin: 15px 0; text-shadow: 0 2px 4px rgba(40,167,69,0.3);
        }
        .city, .rooms { color: #666; margin: 5px 0; }
        .stats { display: flex; gap: 20px; margin-top: 15px; }
        .stat { text-align: center; }
        .stat-number { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .empty { text-align: center; padding: 60px; color: #666; font-size: 1.2rem; }
        .stats-bar {padding: 20px; border-radius: 15px; margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1> Hotel Aggregator</h1>
        
        <div class="filters">
            <div class="filter-row">
                <input id="city" placeholder="Город (Москва, СПб, Сочи...)">
                <input id="min_price" type="number" placeholder="Мин цена" value="0">
                <input id="max_price" type="number" placeholder="Макс цена" value="10000">
                <select id="stars">
                    <option value="">Все звёзды</option>
                    <option value="5">5★</option>
                    <option value="4">4★</option>
                    <option value="3">3★</option>
                </select>
                <input id="min_rooms" type="number" placeholder="Мин номеров">
            </div>
            <button onclick="searchHotels()"> Найти отели</button>
        </div>
        
        <div id="stats" class="stats-bar" style="display:none;"></div>
        <div id="results" class="results"></div>
    </div>

    <script>
    async function searchHotels(page = 1) {
        const params = {
            city: document.getElementById('city').value,
            min_price: parseInt(document.getElementById('min_price').value) || 0,
            max_price: parseInt(document.getElementById('max_price').value) || 999999,
            stars: document.getElementById('stars').value,
            min_rooms: parseInt(document.getElementById('min_rooms').value) || 0,
            page: page,
            limit: 12
        };
        
        document.getElementById('results').innerHTML = 
            '<div class="empty" style="grid-column:1/-1"> Поиск...</div>';
        
        try {
            const url = `/api/hotels?` + new URLSearchParams(params);
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.hotels.length === 0) {
                document.getElementById('results').innerHTML = 
                    '<div class="empty" style="grid-column:1/-1"> Отели не найдены</div>';
            } else {
                let html = '';
                data.hotels.forEach(hotel => {
                    html += `
                        <div class="hotel-card">
                            <div class="hotel-name">${hotel.name} 
                                <span class="stars">${'★'.repeat(hotel.stars)}</span>
                            </div>
                            <div class="city">📍 ${hotel.city}</div>
                            <div class="price">${hotel.price.toLocaleString()}₽ / ночь</div>
                            <div class="rooms">🛏️ ${hotel.available_rooms} номеров свободно</div>
                            <div style="color:#666;margin-top:15px">${hotel.description}</div>
                            <div class="stats">
                                <div class="stat">
                                    <div class="stat-number">${hotel.stars}</div>
                                    <div>★</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-number">${hotel.available_rooms}</div>
                                    <div>номеров</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('results').innerHTML = html;
                
                // Статистика
                document.getElementById('stats').style.display = 'block';
                document.getElementById('stats').innerHTML = `
                    Найдено: <strong>${data.pagination.total}</strong> отелей | 
                    Страница <strong>${data.pagination.page}</strong> из <strong>${data.pagination.pages}</strong> | 
                    Цены: ${params.min_price.toLocaleString()}₽ - ${params.max_price.toLocaleString()}₽
                `;
            }
        } catch(e) {
            document.getElementById('results').innerHTML = 
                '<div class="empty" style="grid-column:1/-1;color:#e74c3c">❌ Ошибка загрузки</div>';
        }
    }
    
    // Автозапуск при загрузке
    searchHotels();
    </script>
</body>
</html>
    ''')

@app.route('/api/hotels', methods=['GET'])
def get_hotels():
    city = request.args.get('city', '').strip()
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 999999, type=int)
    stars = request.args.get('stars')
    min_rooms = request.args.get('min_rooms', 0, type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 12, type=int)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Базовый запрос
    query = "SELECT id, name, city, price, stars, available_rooms, description FROM hotels WHERE price BETWEEN ? AND ?"
    params = [min_price, max_price]
    
    if city:
        query += " AND city LIKE ?"
        params.append(f"%{city}%")
    
    if stars:
        query += " AND stars = ?"
        params.append(int(stars))
    
    if min_rooms:
        query += " AND available_rooms >= ?"
        params.append(min_rooms)
    
    # Подсчёт общего количества
    count_query = query.replace('SELECT id, name, city, price, stars, available_rooms, description', 'SELECT COUNT(*)')
    c.execute(count_query, params)
    total = c.fetchone()[0]
    
    # Пагинация
    offset = (page - 1) * limit
    query += " ORDER BY price ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    c.execute(query, params)
    hotels = []
    for row in c.fetchall():
        hotels.append({
            'id': row[0], 'name': row[1], 'city': row[2], 
            'price': row[3], 'stars': row[4], 'available_rooms': row[5],
            'description': row[6]
        })
    
    conn.close()
    
    return jsonify({
        'success': True,
        'hotels': hotels,
        'filters': {'city': city, 'min_price': min_price, 'max_price': max_price, 'stars': stars},
        'pagination': {'page': page, 'limit': limit, 'total': total, 'pages': (total + limit - 1) // limit}
    })

@app.route('/api/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.execute("SELECT * FROM hotels WHERE id = ?", (hotel_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'hotel': {
                'id': row[0], 'name': row[1], 'city': row[2], 'price': row[3],
                'stars': row[4], 'available_rooms': row[5], 'description': row[6]
            }
        })
    return jsonify({'success': False, 'error': 'Отель не найден'}), 404

if __name__ == '__main__':
    init_db()
    print(" http://localhost:5005")
    print(" API: http://localhost:5005/api/hotels?city=Москва&min_price=3000&max_price=7000")
    app.run(debug=True, port=5005)
