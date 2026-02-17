from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB = "site.db"

# ---------------- DB ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            balance INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            status TEXT DEFAULT 'pending'
        )
        """)

init_db()

# ---------------- HELPERS ----------------
def get_user():
    if "user_id" in session:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
            return cur.fetchone()
    return None

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        try:
            with sqlite3.connect(DB) as con:
                con.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
            return "Kayıt başarılı <a href='/login'>Giriş</a>"
        except:
            return "Kullanıcı var"

    return """
    <h2>Kayıt</h2>
    <form method=post>
    Kullanıcı: <input name=username><br>
    Şifre: <input name=password type=password><br>
    <button>Kayıt</button>
    </form>
    """

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
            user = cur.fetchone()

            if user:
                session["user_id"] = user[0]
                return redirect("/")
            else:
                return "Hatalı giriş"

    return """
    <h2>Giriş</h2>
    <form method=post>
    Kullanıcı: <input name=username><br>
    Şifre: <input name=password type=password><br>
    <button>Giriş</button>
    </form>
    """

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- HOME ----------------
@app.route("/")
def home():
    user = get_user()
    if not user:
        return redirect("/login")

    return f"""
    <h2>Hoşgeldin {user[1]}</h2>
    Bakiye: {user[3]} <br><br>

    <a href='/request'>Bakiye iste</a><br>
    <a href='/myrequests'>İsteklerim</a><br>
    {'<a href="/admin">ADMIN PANEL</a><br>' if user[4]==1 else ''}
    <a href='/logout'>Çıkış</a>
    """

# ---------------- REQUEST BALANCE ----------------
@app.route("/request", methods=["GET","POST"])
def request_balance():
    user = get_user()
    if not user:
        return redirect("/login")

    if request.method == "POST":
        amount = int(request.form["amount"])

        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO requests(user_id,amount) VALUES(?,?)",(user[0],amount))

        return "İstek gönderildi <a href='/'>Geri</a>"

    return """
    <h2>Bakiye İste</h2>
    <form method=post>
    Miktar: <input name=amount><br>
    <button>Gönder</button>
    </form>
    """

# ---------------- MY REQUESTS ----------------
@app.route("/myrequests")
def my_requests():
    user = get_user()
    if not user:
        return redirect("/login")

    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM requests WHERE user_id=?", (user[0],))
        rows = cur.fetchall()

    html = "<h2>İsteklerim</h2>"
    for r in rows:
        html += f"""
        ID:{r[0]} | {r[2]} | {r[3]}
        {'<a href="/cancel/'+str(r[0])+'">İptal</a>' if r[3]=='pending' else ''}
        <br>
        """
    return html + "<br><a href='/'>Geri</a>"

# ---------------- CANCEL REQUEST ----------------
@app.route("/cancel/<int:rid>")
def cancel(rid):
    user = get_user()
    if not user:
        return redirect("/login")

    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM requests WHERE id=? AND user_id=?", (rid,user[0]))

    return redirect("/myrequests")

# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():
    user = get_user()
    if not user or user[4] != 1:
        return "Yetkisiz"

    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("""
        SELECT requests.id, users.username, requests.amount, requests.status, users.id
        FROM requests
        JOIN users ON users.id = requests.user_id
        """)
        rows = cur.fetchall()

    html = "<h2>ADMIN PANEL</h2>"
    for r in rows:
        html += f"""
        ID:{r[0]} | Kullanıcı:{r[1]} | Miktar:{r[2]} | {r[3]}
        <a href='/approve/{r[0]}/{r[4]}/{r[2]}'>Onay</a>
        <a href='/deny/{r[0]}'>Red</a>
        <br>
        """
    return html + "<br><a href='/'>Geri</a>"

# ---------------- APPROVE ----------------
@app.route("/approve/<int:rid>/<int:uid>/<int:amount>")
def approve(rid, uid, amount):
    user = get_user()
    if not user or user[4] != 1:
        return "Yetkisiz"

    with sqlite3.connect(DB) as con:
        con.execute("UPDATE requests SET status='approved' WHERE id=?", (rid,))
        con.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, uid))

    return redirect("/admin")

# ---------------- DENY ----------------
@app.route("/deny/<int:rid>")
def deny(rid):
    user = get_user()
    if not user or user[4] != 1:
        return "Yetkisiz"

    with sqlite3.connect(DB) as con:
        con.execute("UPDATE requests SET status='denied' WHERE id=?", (rid,))

    return redirect("/admin")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
