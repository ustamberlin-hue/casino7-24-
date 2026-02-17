import os
import sqlite3
import random
from flask import Flask, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "batak_vip_exclusive_2024"
DB = "site.db"

# ---------------- DATABASE INIT ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        # Kullanıcılar Tablosu (Varsayılan bakiye 1000)
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            balance INTEGER DEFAULT 1000,
            is_admin INTEGER DEFAULT 0
        )""")
        # Bakiye İstekleri Tablosu
        cur.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            status TEXT DEFAULT 'pending'
        )""")
        # İlk Admini Oluştur (admin / 1234)
        cur.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('admin', '1234', 1)")
init_db()

# ---------------- HELPERS ----------------
def get_user():
    if "user_id" in session:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
            return cur.fetchone()
    return None

def batak_motoru():
    # Bot ve Oyun Mantığı: Basitleştirilmiş Batak Simülasyonu
    oyuncular = ["Siz", "Bot_Mert", "Bot_Selin", "Bot_Caner"]
    skorlar = {o: random.randint(1, 13) for o in oyuncular} # Rastgele el alma
    kazanan = max(skorlar, key=skorlar.get)
    return kazanan, skorlar

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    user = get_user()
    if not user: return redirect(url_for('login'))
    return f"""
    <div style="font-family:sans-serif; text-align:center;">
        <h2>🃏 Batak Salonu</h2>
        <p>Hoşgeldin <b>{user[1]}</b> | Bakiye: <b>{user[3]} TL</b></p>
        <hr>
        <a href="/play"><button style="padding:10px 20px; background:green; color:white; border:none; border-radius:5px; cursor:pointer;">HIZLI MASAYA OTUR (100 TL)</button></a><br><br>
        <a href="/request">Bakiye Yükle</a> | <a href="/settings">Şifre Değiştir</a> | <a href="/logout">Çıkış</a>
        {"<br><br><a href='/admin' style='color:red;'>RED ADMIN PANEL</a>" if user[4]==1 else ""}
    </div>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['u'], request.form['p']
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            user = cur.fetchone()
            if user:
                session["user_id"] = user[0]
                return redirect(url_for('home'))
        return "Hatalı Giriş! <a href='/login'>Tekrar Dene</a>"
    return '''<body style="text-align:center; font-family:sans-serif;"><h2>Giriş Yap</h2>
    <form method="post">Kullanıcı: <input name="u"><br><br>Şifre: <input name="p" type="password"><br><br><button>Giriş</button></form>
    <br><a href="/register">Kayıt Ol</a></body>'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form['u'], request.form['p']
        try:
            with sqlite3.connect(DB) as con:
                con.execute("INSERT INTO users(username,password) VALUES(?,?)", (u, p))
            return "Kayıt Başarılı! <a href='/login'>Giriş yapın</a>"
        except: return "Kullanıcı adı alınmış!"
    return '<body style="text-align:center;"><h2>Kayıt Ol</h2><form method="post">Kullanıcı: <input name="u"><br><br>Şifre: <input name="p" type="password"><br><br><button>Kayıt Ol</button></form></body>'

@app.route('/play')
def play():
    user = get_user()
    if not user or user[3] < 100: return "Yetersiz bakiye! En az 100 TL gerekir. <a href='/'>Geri</a>"
    
    kazanan, detaylar = batak_motoru()
    mesaj = f"Masa kuruldu: Siz, Mert, Selin, Caner.<br>Oyun bitti! <b>Kazanan: {kazanan}</b><br><br>"
    for isim, el in detaylar.items():
        mesaj += f"{isim}: {el} el aldı.<br>"

    with sqlite3.connect(DB) as con:
        if kazanan == "Siz":
            con.execute("UPDATE users SET balance = balance + 200 WHERE id=?", (user[0],))
            mesaj = "🎉 TEBRİKLER! 200 TL Kazandınız!<br>" + mesaj
        else:
            con.execute("UPDATE users SET balance = balance - 100 WHERE id=?", (user[0],))
            mesaj = "😔 Kaybettiniz. 100 TL Bakiyenizden düştü.<br>" + mesaj
    
    return mesaj + "<br><a href='/play'>Tekrar Oyna</a> | <a href='/'>Ana Sayfa</a>"

@app.route('/admin')
def admin():
    user = get_user()
    if not user or user[4] != 1: return "Yetkisiz Erişim!"
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT requests.id, users.username, requests.amount FROM requests JOIN users ON users.id = requests.user_id WHERE requests.status='pending'")
        reqs = cur.fetchall()
    html = "<h2>Admin Onay Paneli</h2>"
    for r in reqs:
        html += f"ID:{r[0]} | {r[1]} - {r[2]} TL <a href='/approve/{r[0]}'>[ONAYLA]</a><br>"
    return html + "<br><a href='/'>Geri</a>"

@app.route('/approve/<int:rid>')
def approve(rid):
    user = get_user()
    if not user or user[4] != 1: return "Yetkisiz"
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT user_id, amount FROM requests WHERE id=?", (rid,))
        res = cur.fetchone()
        if res:
            con.execute("UPDATE users SET balance = balance + ? WHERE id=?", (res[1], res[0]))
            con.execute("UPDATE requests SET status='approved' WHERE id=?", (rid,))
    return redirect(url_for('admin'))

@app.route('/request', methods=['GET', 'POST'])
def request_money():
    user = get_user()
    if not user: return redirect(url_for('login'))
    if request.method == 'POST':
        amt = request.form['amt']
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO requests(user_id, amount) VALUES(?,?)", (user[0], amt))
        return "Talebiniz iletildi, admin onayı bekleniyor. <a href='/'>Geri</a>"
    return '<h2>Bakiye Talebi</h2><form method="post">Miktar: <input name="amt"><button>Gönder</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
