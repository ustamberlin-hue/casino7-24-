import os, sqlite3, random
from flask import Flask, request, redirect, session, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "batak_masa_2024"
DB = "site.db"

# ---------------- DATABASE ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, balance INTEGER DEFAULT 1000, is_admin INTEGER DEFAULT 0)")
        cur.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('admin', '1234', 1)")
init_db()

# ---------------- GAME LOGIC ----------------
def yeni_desteyi_dagit():
    renkler = ['♠️', '♣️', '♦️', '♥️']
    sayilar = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deste = [f"{s}{r}" for r in renkler for s in sayilar]
    random.shuffle(deste)
    return [sorted(deste[i:i+13]) for i in range(0, 52, 13)]

# ---------------- HTML TASARIM (MASA) ----------------
MASA_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #2c3e50; color: white; font-family: sans-serif; text-align: center; }
        .table { 
            background: #27ae60; width: 80%; height: 500px; margin: 50px auto; 
            border-radius: 200px; border: 15px solid #7e5233; position: relative;
        }
        .player { position: absolute; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 10px; }
        .top { top: 20px; left: 45%; }
        .left { top: 45%; left: 20px; }
        .right { top: 45%; right: 20px; }
        .bottom { bottom: 20px; left: 35%; width: 30%; }
        .center-pot { 
            position: absolute; top: 35%; left: 35%; width: 30%; height: 30%;
            border: 2px dashed white; border-radius: 10px; display: flex; align-items: center; justify-content: center;
        }
        .card { 
            background: white; color: black; padding: 10px; border-radius: 5px; 
            margin: 5px; display: inline-block; cursor: pointer; border: 1px solid #000;
        }
        .card:hover { background: #f1c40f; }
        .played-card { background: white; color: black; padding: 15px; border-radius: 5px; margin: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Bakiye: {{ user[3] }} TL</h2>
    <div class="table">
        <div class="player top">Bot Ece</div>
        <div class="player left">Bot admin</div>
        <div class="player right">Bot Derya</div>
        
        <div class="center-pot">
            {% for c in masa %}
                <div class="played-card">{{ c }}</div>
            {% endfor %}
            {% if not masa %} <p>Kart Bekleniyor...</p> {% endif %}
        </div>

        <div class="bottom">
            <p>Siz (Emre)</p>
            {% for i, c in enumerate(elim) %}
                <a href="/play_card/{{ i }}" style="text-decoration:none;">
                    <div class="card">{{ c }}</div>
                </a>
            {% endfor %}
        </div>
    </div>
    <a href="/logout" style="color:white;">Masadan Kalk</a>
</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    if "user_id" not in session: return redirect('/login')
    with sqlite3.connect(DB) as con:
        user = con.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    
    # Bakiye kontrolü ve oyun başlatma
    if 'elim' not in session:
        con.execute("UPDATE users SET balance = balance - 100 WHERE id=?", (session["user_id"],))
        eller = yeni_desteyi_dagit()
        session['elim'], session['bot1'], session['bot2'], session['bot3'] = eller
        session['masa'] = []
    
    return render_template_string(MASA_HTML, user=user, elim=session['elim'], masa=session['masa'], enumerate=enumerate)

@app.route('/play_card/<int:idx>')
def play_card(idx):
    elim = session.get('elim', [])
    if not elim: return redirect('/')
    
    kart = elim.pop(idx)
    # Botlar da birer kart atar
    b1, b2, b3 = session['bot1'].pop(0), session['bot2'].pop(0), session['bot3'].pop(0)
    
    session['elim'] = elim
    session['masa'] = [kart, b1, b2, b3]
    
    if not elim: session.pop('elim') # Oyun bittiğinde sıfırla
    return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        with sqlite3.connect(DB) as con:
            user = con.execute("SELECT * FROM users WHERE username=? AND password=?", (request.form['u'], request.form['p'])).fetchone()
            if user:
                session["user_id"] = user[0]
                return redirect('/')
    return '<form method="post">Admin: <input name="u"> Şifre: <input name="p" type="password"><button>Giriş</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
