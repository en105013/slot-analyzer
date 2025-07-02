
from flask import Flask, render_template, request, redirect
import sqlite3
import time

app = Flask(__name__)

# 安全型轉換函式
def safe_int(value):
    try:
        return int(value)
    except:
        return 0

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

DATABASE = 'slot_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS slot_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            no_bonus_spin INTEGER,
            last_bonus_spin INTEGER,
            second_last_bonus_spin INTEGER,
            today_rtp REAL,
            last30_rtp REAL,
            today_bet INTEGER,
            last30_bet INTEGER,
            score REAL,
            status TEXT,
            suggestion TEXT,
            recommended_bet INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO slot_records (
                name, no_bonus_spin, last_bonus_spin, second_last_bonus_spin,
                today_rtp, last30_rtp, today_bet, last30_bet, score,
                status, suggestion, recommended_bet, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            safe_int(data.get('no_bonus_spin')),
            safe_int(data.get('last_bonus_spin')),
            safe_int(data.get('second_last_bonus_spin')),
            safe_float(data.get('today_rtp')),
            safe_float(data.get('last30_rtp')),
            safe_int(data.get('today_bet')),
            safe_int(data.get('last30_bet')),
            safe_float(data.get('score')),
            data.get('status'),
            data.get('suggestion'),
            safe_int(data.get('recommended_bet')),
            data['timestamp']
        ))
        conn.commit()
        conn.close()
        return redirect('/records')
    return render_template('index.html')

@app.route('/records')
def records():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM slot_records ORDER BY id DESC")
    records = c.fetchall()
    conn.close()
    return render_template('records.html', records=records)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
