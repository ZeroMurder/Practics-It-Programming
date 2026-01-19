from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'schedule.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  БД удалена")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблицы
    c.execute('''CREATE TABLE groups (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE teachers (id INTEGER PRIMARY KEY, full_name TEXT)''')
    c.execute('''CREATE TABLE rooms (id INTEGER PRIMARY KEY, number TEXT UNIQUE, capacity INTEGER)''')
    c.execute('''CREATE TABLE subjects (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE lessons (
        id INTEGER PRIMARY KEY,
        group_id INTEGER, teacher_id INTEGER, room_id INTEGER, subject_id INTEGER,
        weekday INTEGER CHECK (weekday BETWEEN 1 AND 7),
        lesson_number INTEGER CHECK (lesson_number BETWEEN 1 AND 6),
        UNIQUE(group_id, weekday, lesson_number),
        UNIQUE(teacher_id, weekday, lesson_number),
        UNIQUE(room_id, weekday, lesson_number)
    )''')
    
    # Данные
    c.executemany("INSERT INTO groups(id, name) VALUES (?, ?)", [(1, "А-101"), (2, "Б-202"), (3, "ИТ-301")])
    c.executemany("INSERT INTO teachers(id, full_name) VALUES (?, ?)", [(1, "Иванов И.И."), (2, "Петров П.П."), (3, "Сидорова А.А.")])
    c.executemany("INSERT INTO rooms(id, number, capacity) VALUES (?, ?, ?)", [(1, "101", 30), (2, "205", 25), (3, "Лаб-3", 20)])
    c.executemany("INSERT INTO subjects(id, name) VALUES (?, ?)", [(1, "Математика"), (2, "Физика"), (3, "Программирование")])
    
    conn.commit()
    conn.close()
    print(" БД готова!")

def can_schedule(group_id, teacher_id, room_id, weekday, lesson_num):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT 1 FROM lessons WHERE group_id=? AND weekday=? AND lesson_number=?", (group_id, weekday, lesson_num))
    if c.fetchone(): return False, "Группа занята"
    
    c.execute("SELECT 1 FROM lessons WHERE teacher_id=? AND weekday=? AND lesson_number=?", (teacher_id, weekday, lesson_num))
    if c.fetchone(): return False, "Преподаватель занят"
    
    c.execute("SELECT 1 FROM lessons WHERE room_id=? AND weekday=? AND lesson_number=?", (room_id, weekday, lesson_num))
    if c.fetchone(): return False, "Аудитория занята"
    
    conn.close()
    return True, "OK"

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Расписание занятий</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        select, input, button { padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 10px; }
        button { background: #28a745; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #218838; }
        .message.success { background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; margin: 15px 0; }
        .message.error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin: 15px 0; }
        .schedule { background: #f8f9fa; padding: 20px; border-radius: 10px; }
        .lesson { padding: 15px; margin: 10px 0; background: white; border-radius: 8px; border-left: 4px solid #007bff; }
        .weekday-btn { margin: 5px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 20px; cursor: pointer; }
        .weekday-btn.active { background: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1> Расписание занятий</h1>
        
        <div class="form-grid">
            <select id="group"><option value="">Группа</option><option value="1">А-101</option><option value="2">Б-202</option><option value="3">ИТ-301</option></select>
            <select id="teacher"><option value="">Преподаватель</option><option value="1">Иванов И.И.</option><option value="2">Петров П.П.</option><option value="3">Сидорова А.А.</option></select>
            <select id="room"><option value="">Аудитория</option><option value="1">101 (30 мест)</option><option value="2">205 (25 мест)</option><option value="3">Лаб-3 (20 мест)</option></select>
            <select id="subject"><option value="">Предмет</option><option value="1">Математика</option><option value="2">Физика</option><option value="3">Программирование</option></select>
            <select id="weekday"><option value="">День недели</option><option value="1">Понедельник</option><option value="2">Вторник</option><option value="3">Среда</option><option value="4">Четверг</option><option value="5">Пятница</option></select>
            <select id="lesson"><option value="">Пара</option><option value="1">1-я (8:30)</option><option value="2">2-я (10:00)</option><option value="3">3-я (11:30)</option><option value="4">4-я (13:30)</option><option value="5">5-я (15:10)</option><option value="6">6-я (16:40)</option></select>
            <button onclick="addLesson()"> Запланировать</button>
        </div>
        
        <div id="message"></div>
        
        <div style="text-align: center; margin: 30px 0;">
            <button class="weekday-btn active" onclick="loadSchedule(1)">Пн</button>
            <button class="weekday-btn" onclick="loadSchedule(2)">Вт</button>
            <button class="weekday-btn" onclick="loadSchedule(3)">Ср</button>
            <button class="weekday-btn" onclick="loadSchedule(4)">Чт</button>
            <button class="weekday-btn" onclick="loadSchedule(5)">Пт</button>
        </div>
        
        <div id="schedule" class="schedule">
            <h3> Расписание (Понедельник)</h3>
            <p>Выберите день или добавьте занятие</p>
        </div>
    </div>

    <script>
    async function addLesson() {
        const data = {
            group_id: parseInt(document.getElementById('group').value),
            teacher_id: parseInt(document.getElementById('teacher').value),
            room_id: parseInt(document.getElementById('room').value),
            subject_id: parseInt(document.getElementById('subject').value),
            weekday: parseInt(document.getElementById('weekday').value),
            lesson_number: parseInt(document.getElementById('lesson').value)
        };
        
        if (!data.group_id || !data.teacher_id || !data.room_id || !data.subject_id || !data.weekday || !data.lesson_number) {
            showMessage('Заполните все поля!', 'error');
            return;
        }
        
        try {
            const res = await fetch('/api/schedule', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            
            showMessage(result.success ? '✅ ' + result.message : ' ' + result.error, 
                       result.success ? 'success' : 'error');
            
            if (result.success) document.querySelector('.form-grid').reset();
            loadSchedule(data.weekday);
        } catch(e) {
            showMessage('Ошибка сервера', 'error');
        }
    }
    
    function showMessage(text, type) {
        document.getElementById('message').innerHTML = `<div class="message ${type}">${text}</div>`;
        setTimeout(() => document.getElementById('message').innerHTML = '', 5000);
    }
    
    async function loadSchedule(weekday) {
        document.querySelectorAll('.weekday-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        
        const res = await fetch(`/api/schedule?weekday=${weekday}`);
        const data = await res.json();
        
        let html = `<h3> Расписание (${['','Пн','Вт','Ср','Чт','Пт'][weekday]})</h3>`;
        if (data.schedule.length === 0) {
            html += '<p>Занятий нет</p>';
        } else {
            data.schedule.forEach(l => {
                html += `
                    <div class="lesson">
                        <strong>${l.group}</strong> | ${l.teacher} | 
                        <strong>${l.room}</strong> | ${l.subject}
                        <span style="float:right">${l.lesson}-я пара</span>
                    </div>
                `;
            });
        }
        document.getElementById('schedule').innerHTML = html;
    }
    </script>
</body>
</html>
    ''')

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    weekday = request.args.get('weekday', 1, type=int)
    conn = sqlite3.connect(DB_PATH)
    c = conn.execute('''
        SELECT g.name, t.full_name, r.number, s.name, l.weekday, l.lesson_number
        FROM lessons l JOIN groups g ON l.group_id=g.id
        JOIN teachers t ON l.teacher_id=t.id
        JOIN rooms r ON l.room_id=r.id
        JOIN subjects s ON l.subject_id=s.id
        WHERE l.weekday=?
        ORDER BY l.lesson_number
    ''', (weekday,))
    
    schedule = [{'group':r[0], 'teacher':r[1], 'room':r[2], 'subject':r[3], 
                'weekday':r[4], 'lesson':r[5]} for r in c.fetchall()]
    conn.close()
    return jsonify({'schedule': schedule})

@app.route('/api/schedule', methods=['POST'])
def create_lesson():
    data = request.json
    ok, msg = can_schedule(data['group_id'], data['teacher_id'], data['room_id'], 
                          data['weekday'], data['lesson_number'])
    
    if not ok:
        return jsonify({'success': False, 'error': msg}), 409
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO lessons(group_id, teacher_id, room_id, subject_id, weekday, lesson_number)
                 VALUES(?,?,?,?,?,?)''', (data['group_id'], data['teacher_id'], data['room_id'],
                                         data['subject_id'], data['weekday'], data['lesson_number']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Занятие запланировано'})

if __name__ == '__main__':
    init_db()
    print(" http://localhost:5010")
    print(" Расписание с защитой от конфликтов!")
    app.run(debug=True, port=5010)
