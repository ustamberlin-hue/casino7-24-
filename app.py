import random
import os
from datetime import datetime
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "gokay_casino_empire_v3_premium"

# --- VERİ TABANI ---
db = {
    "users": {
        "admin": {"pw": "1234", "role": "ADMIN", "ad": "Patron", "bakiye": 1000000}
    },
    "basvurular": [],
    "bakiye_talepleri": []
}

def format_euro(value):
    return "{:,.2f} €".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

OYUNLAR = [
    {"id": "sweet_bonanza", "ad": "Sweet Bonanza", "img": "https://i.ibb.co/L6V2MvL/slot3.jpg"},
    {"id": "gates_olympus", "ad": "Gates of Olympus", "img": "https://i.ibb.co/f2PzC6z/slot2.jpg"},
    {"id": "fruit_party", "ad": "Fruit Party", "img": "https://i.ibb.co/hZz00fV/slot1.jpg"},
    {"id": "dog_house", "ad": "The Dog House", "img": "https://i.ibb.co/L6V2MvL/slot3.jpg"},
    {"id": "sugar_rush", "ad": "Sugar Rush", "img": "https://i.ibb.co/f2PzC6z/slot2.jpg"}
] # (20 oyun listesini görsel kartlar için kısa tuttum, hepsini ekleyebilirsin)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
        .header { background:linear-gradient(90deg, #fcd535, #ffb800); color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:#16181c; margin:10px; padding:15px; border-radius:12px; border:1px solid #333; }
        .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding:10px; }
        .game-card { background:#1c1f26; border-radius:12px; overflow:hidden; border:1px solid #333; text-align:center; cursor:pointer; }
        .game-card img { width:100%; height:100px; object-fit:cover; }
        .btn { background:#fcd535; color:black; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer; }
        .btn-red { background:#ff4444; color:white; }
        .btn-green { background:#0ecb81; color:white; }
        .input { width:100%; padding:12px; margin-bottom:10px; background:black; color:white; border:1px solid #333; border-radius:8px; box-sizing:border-box; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; }
        .nav-btn { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:12px; }
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
    </style>
</head>
<body>
    <div class="header">🏢 GOKAYBETT CASINO LOBBY</div>

    {% if not session.user %}
        <div style="padding:30px;">
            {% if request.args.get('m') == 'kayit' %}
                <h3>Üyelik Başvurusu</h3>
                <form action="/islem/kayit" method="post">
                    <input type="text" name="ad" placeholder="Ad Soyad" class="input" required>
                    <input type="text" name="u" placeholder="Kullanıcı Adı" class="input" required>
                    <input type="password" name="p" placeholder="Şifre" class="input" required>
                    <button class="btn">BAŞVURU GÖNDER</button>
                    <a href="/" style="color:#fcd535; display:block; text-align:center; margin-top:15px;">Giriş Yap</a>
                </form>
            {% else %}
                <h3>Terminal Girişi</h3>
                {% if request.args.get('e') %}<p style="color:red;">Hatalı giriş veya onay bekleyen üyelik!</p>{% endif %}
                <form action="/islem/giris" method="post">
                    <input type="text" name="u" placeholder="Kullanıcı Adı" class="input" required>
                    <input type="password" name="p" placeholder="Şifre" class="input" required>
                    <button class="btn">SİSTEME GİRİŞ</button>
                    <a href="/?m=kayit" style="color:#fcd535; display:block; text-align:center; margin-top:15px;">Üyelik Başvurusu Yap</a>
                </form>
            {% endif %}
        </div>
    {% else %}
        {% if p == 'ADMIN' and session.user == 'admin' %}
            <div style="padding:10px;">
                <h3>Yönetim Paneli</h3>
                <h4>Üyelik Bekleyenler</h4>
                {% for b in db.basvurular %}
                    <div class="card">
                        {{ b.ad }} (@{{ b.u }})
                        <div style="display:flex; gap:5px; margin-top:10px;">
                            <a href="/admin/onay/{{ loop.index0 }}" class="btn btn-green">ONAY</a>
                            <a href="/admin/red/{{ loop.index0 }}" class="btn btn-red">RED</a>
                        </div>
                    </div>
                {% endfor %}
                <h4>Bakiye Talepleri</h4>
                {% for t in db.bakiye_talepleri %}
                    <div class="card">
                        {{ t.u }}: {{ t.m }} €
                        <div style="display:flex; gap:5px; margin-top:10px;">
                            <a href="/admin/b_onay/{{ loop.index0 }}" class="btn btn-green">YÜKLE</a>
                            <a href="/admin/b_red/{{ loop.index0 }}" class="btn btn-red">İPTAL</a>
                        </div>
                    </div>
                {% endfor %}
                <h4>Aktif Üyeler</h4>
                {% for u_name, u_info in db.users.items() %}
                    <div class="card" style="font-size:12px;">
                        <b>{{ u_info.ad }}</b> (@{{ u_name }}) - Bakiye: {{ u_info.bakiye }} €
                    </div>
                {% endfor %}
            </div>
        {% elif p == 'PROFIL' %}
            <div class="card">
                <h3>Hesap Ayarları</h3>
                <p>Bakiyeniz: <b>{{ fmt(bakiye) }}</b></p>
                <hr border="0.1">
                <h4>Şifre Değiştir</h4>
                <form action="/islem/sifre" method="post">
                    <input type="password" name="p" placeholder="Yeni Şifre" class="input" required>
                    <button class="btn">GÜNCELLE</button>
                </form>
                <hr border="0.1">
                <h4>Bakiye Talep Et</h4>
                <form action="/islem/bakiye_iste" method="post">
                    <input type="number" name="m" placeholder="Miktar €" class="input" required>
                    <button class="btn btn-green">TALEP GÖNDER</button>
                </form>
            </div>
        {% else %}
            <div class="card" style="text-align:center; border-left:4px solid #fcd535;">
                BAKİYE: <b style="color:#0ecb81; font-size:20px;">{{ fmt(bakiye) }}</b>
            </div>
            <div class="grid">
                {% for g in oyunlar %}
                <div class="game-card" onclick="alert('Oyun Başlatılıyor: {{g.ad}}')">
                    <img src="{{ g.img }}">
                    <div style="padding:5px; font-size:11px;">{{ g.ad }}</div>
                </div>
                {% endfor %}
            </div>
        {% endif %}

        <div class="nav">
            <a href="/" class="nav-btn">🎰 OYUNLAR</a>
            <a href="/p/PROFIL" class="nav-btn">👤 PROFİL</a>
            {% if session.user == 'admin' %}<a href="/p/ADMIN" class="nav-btn" style="color:#fcd535;">⚙️ PANEL</a>{% endif %}
            <a href="/logout" class="nav-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
@app.route('/p/<p>')
def index(p='LOBBY'):
    u = session.get("user")
    u_data = db["users"].get(u, {"bakiye":0})
    return render_template_string(HTML, p=p, bakiye=u_data['bakiye'], oyunlar=OYUNLAR, db=db, fmt=format_euro)

@app.route('/islem/<aksiyon>', methods=['POST'])
def islem(aksiyon):
    if aksiyon == "giris":
        u, p = request.form.get('u', '').lower(), request.form.get('p')
        if u in db["users"] and db["users"][u]["pw"] == p:
            session["user"] = u
            return redirect('/')
        return redirect('/?e=1')
    
    if aksiyon == "kayit":
        u = request.form.get('u', '').lower()
        if u in db["users"] or any(b['u'] == u for b in db["basvurular"]):
            return "Bu kullanıcı adı zaten alınmış!"
        db["basvurular"].append({"u": u, "p": request.form.get('p'), "ad": request.form.get('ad')})
        return "Başvurunuz alındı, admin onayı bekleniyor."

    if session.get("user"):
        u = session["user"]
        if aksiyon == "sifre":
            db["users"][u]["pw"] = request.form.get('p')
        elif aksiyon == "bakiye_iste":
            db["bakiye_talepleri"].append({"u": u, "m": float(request.form.get('m', 0))})
    return redirect('/')

@app.route('/admin/<aksiyon>/<int:id>')
def admin_islem(aksiyon, id):
    if session.get("user") == "admin":
        if aksiyon == "onay":
            b = db["basvurular"].pop(id)
            db["users"][b['u']] = {"pw": b['p'], "ad": b['ad'], "bakiye": 0}
        elif aksiyon == "red":
            db["basvurular"].pop(id)
        elif aksiyon == "b_onay":
            t = db["bakiye_talepleri"].pop(id)
            if t['u'] in db["users"]: db["users"][t['u']]["bakiye"] += t['m']
        elif aksiyon == "b_red":
            db["bakiye_talepleri"].pop(id)
    return redirect('/p/ADMIN')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
