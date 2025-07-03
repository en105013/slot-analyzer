
from flask import Flask, render_template, request, redirect
import sqlite3
import time

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

app = Flask(__name__)
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

        # 數值轉換
        no_bonus_spin = safe_int(data.get('no_bonus_spin'))
        last_bonus_spin = safe_int(data.get('last_bonus_spin'))
        second_last_bonus_spin = safe_int(data.get('second_last_bonus_spin'))
        today_rtp = safe_float(data.get('today_rtp'))
        last30_rtp = safe_float(data.get('last30_rtp'))
        today_bet = safe_int(data.get('today_bet'))
        last30_bet = safe_int(data.get('last30_bet'))
        base = 1e-5 if last30_bet == 0 else last30_bet

        # 🔍 自動計算 score
        rtp_score = (today_rtp + last30_rtp) / 2
        spin_score = (last_bonus_spin + second_last_bonus_spin) / 2 if last_bonus_spin > 0 else 0
        bet_score = today_bet / base
        score = round(rtp_score * 0.6 + spin_score * 0.001 + bet_score * 0.3, 4)

        # 🔍 自動判斷狀態與建議
        status = "高潛力" if score > 1.1 else "觀望" if score > 0.9 else "低爆機率"
        suggestion = "建議進場" if score > 1.1 else "可小注觀察" if score > 0.9 else "不建議"

        # 🔍 推薦下注金額（以你輸入的本金計算）
        bankroll = safe_int(data.get("bankroll"))
        recommended_bet = int(bankroll * 0.02) if bankroll > 0 else 0

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
            no_bonus_spin,
            last_bonus_spin,
            second_last_bonus_spin,
            today_rtp,
            last30_rtp,
            today_bet,
            last30_bet,
            score,
            status,
            suggestion,
            recommended_bet,
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
