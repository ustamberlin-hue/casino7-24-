import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_patron_exclusive"

# --- VERİ TABANI ---
db = {
    "users": {
        "admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}
    },
    "basvurular": [],
    "bakiye_talepleri": []
}

# --- OYUN AYARLARI ---
OYUN_DATA = {
    "Sweet Bonanza": {"s": ["🍭", "🍉", "🍎", "🍇", "🍌"], "bg": "#ff75bd", "win_text": "🍭 ŞEKER PATLAMASI!"},
    "Gates of Olympus": {"s": ["⚡", "👑", "💍", "🍷", "💎"], "bg": "#4b0082", "win_text": "⚡ ZEUS ÇARPTI!"},
    "The Dog House": {"s": ["🐶", "🦴", "🏠", "🐕", "🐾"], "bg": "#8b4513", "win_text": "🐾 HAV HAV KAZANÇ!"},
    "Big Bass Bonanza": {"s": ["🐟", "🎣", "🛶", "🛟", "🐠"], "bg": "#0077be", "win_text": "🎣 BÜYÜK BALIK!"},
    "Sugar Rush": {"s": ["🧸", "🍬", "🧁", "🍩", "🍭"], "bg": "#db7093", "win_text": "🧸 REÇEL DOLU!"},
    "Wanted Dead or Wild": {"s": ["🤠", "🔫", "🥃", "🌵", "💰"], "bg": "#3d2b1f", "win_text": "🔫 DÜELLO!"},
    "Starlight Princess": {"s": ["⭐", "💖", "🌙", "👑", "🔮"], "bg": "#1e90ff", "win_text": "⭐ YILDIZ GÜCÜ!"},
    "Wolf Gold": {"s": ["🐺", "🌙", "🦅", "🐂", "🐎"], "bg": "#2f4f4f", "win_text": "🐺 ULUMA BONUSU!"},
    "Buffalo King": {"s": ["🦬", "🦅", "🐺", "🏜️", "🔥"], "bg": "#d2691e", "win_text": "🏜️ VAHŞİ KAZANÇ!"},
    "Book of Dead": {"s": ["📖", "⚱️", "🗿", "🐍", "🎭"], "bg": "#4a3b22", "win_text": "📖 ANTİK HAZİNE!"}
}

OYUNLAR = [
    {"ad": "Sweet Bonanza", "img": "https://img.freepik.com/premium-photo/colorful-candies-sweets-falling-into-slot-machine-generative-ai_175880-1430.jpg"},
    {"ad": "Gates of Olympus", "img": "https://img.freepik.com/free-photo/god-zeus-concept-illustration_23-2150534293.jpg"},
    {"ad": "The Dog House", "img": "https://img.freepik.com/free-photo/cute-puppy-house-concept_23-2150166254.jpg"},
    {"ad": "Big Bass Bonanza", "img": "https://img.freepik.com/premium-photo/fishing-hobby-professional-equipment-generative-ai_175880-1500.jpg"},
    {"ad": "Sugar Rush", "img": "https://img.freepik.com/premium-photo/pink-candyland-abstract-background-generative-ai_175880-1200.jpg"},
    {"ad": "Wanted Dead or Wild", "img": "https://img.freepik.com/free-photo/wild-west-wanted-poster-vintage_23-2150166600.jpg"},
    {"ad": "Starlight Princess", "img": "https://img.freepik.com/premium-photo/anime-princess-starry-night-generative-ai_175880-1600.jpg"},
    {"ad": "Wolf Gold", "img": "https://img.freepik.com/free-photo/wolf-concept-illustration_23-2150166540.jpg"},
    {"ad": "Buffalo King", "img": "https://img.freepik.com/free-photo/majestic-buffalo-wilderness_23-2150166700.jpg"},
    {"ad": "Book of Dead", "img": "https://img.freepik.com/free-photo/egypt-concept-illustration_114360-2123.jpg"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; padding-bottom:100px; }
        .header { background:#fcd535; color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:#16181c; margin:10px; padding:15px; border-radius:12px; border:1px solid #333; }
        .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding:10px; }
        .game-card { background:#1c1f26; border-radius:12px; overflow:hidden; border:1px solid #444; cursor:pointer; }
        .game-card img { width:100%; height:120px; object-fit:cover; }
        .btn { background:#fcd535; color:black; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer; }
        .leaderboard { background:#16181c; margin:15px; border-radius:10px; padding:10px; border:1px solid #fcd535; }
        .user-row { display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid #333; font-size:14px; }
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
        .slot-content { width:85%; max-width:400px; padding:20px; border-radius:20px; border:3px solid #fcd535; text-align:center; }
        .reels { display:flex; justify-content:center; gap:10px; margin:20px 0; }
        .reel { background:rgba(0,0,0,0.6); width:70px; height:80px; display:flex; align-items:center; justify-content:center; font-size:40px; border-radius:10px; border:1px solid #555; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; z-index:99; }
        .nav-link { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:12px; }
    </style>
</head>
<body>
    <div class="header">💎 CASINO7-24 PATRON PANEL</div>

    {% if not session.user %}
        <div style="padding:30px;">
            <h3>Giriş / Kayıt</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı" required style="width:100%; padding:12px; margin-bottom:10px; background:black; color:white;">
                <input type="password" name="p" placeholder="Şifre" required style="width:100%; padding:12px; margin-bottom:10px; background:black; color:white;">
                <button name="act" value="in" class="btn">GİRİŞ YAP</button><br><br>
                <button name="act" value="up" class="btn" style="background:#555; color:white;">KAYIT OL (ONAY GEREKİR)</button>
            </form>
        </div>
    {% else %}
        {% if p == 'ADMIN' %}
            <div style="padding:15px;">
                <h3>⚙️ Admin Paneli</h3>
                <p>Bekleyen Başvurular:</p>
                {% for b in db.basvurular %}
                    <div class="card">{{ b.u }} <a href="/admin/onay/{{loop.index0}}" style="color:lime;">[ONAY]</a></div>
                {% endfor %}
                <p>Bakiye Talepleri:</p>
                {% for t in db.bakiye_talepleri %}
                    <div class="card">{{ t.u }}: {{ t.amt }} € <a href="/admin/bakiye/{{loop.index0}}" style="color:lime;">[YÜKLE]</a></div>
                {% endfor %}
            </div>
        {% elif p == 'CASH' %}
            <div style="padding:30px; text-align:center;">
                <h3>💰 Bakiye Yükle</h3>
                <form action="/talep" method="post">
                    <input type="number" name="amt" placeholder="Miktar (Euro)" required style="width:100%; padding:15px; margin-bottom:20px; background:black; color:white;">
                    <button class="btn">TALEP GÖNDER</button>
                </form>
            </div>
        {% else %}
            <div class="card" style="text-align:center;">
                <span style="color:#aaa;">Bakiyeniz:</span><br>
                <b id="main-bal" style="color:#0ecb81; font-size:28px;">{{ user.bakiye }} €</b>
            </div>
            <div class="grid">
                {% for g in oyunlar %}
                <div class="game-card" onclick="openSlot('{{ g.ad }}')">
                    <img src="{{ g.img }}">
                    <div style="padding:8px; text-align:center; font-weight:bold;">{{ g.ad }}</div>
                </div>
                {% endfor %}
            </div>
            <div class="leaderboard">
                <div style="text-align:center; color:#fcd535; font-weight:bold; margin-bottom:10px;">👥 TÜM OYUNCULAR</div>
                {% for name, data in db.users.items() %}
                <div class="user-row"><span>{{ name }}</span><b>{{ data.bakiye }} €</b></div>
                {% endfor %}
            </div>
        {% endif %}

        <div class="nav">
            <a href="/" class="nav-link">🎰 OYUNLAR</a>
            <a href="/?p=CASH" class="nav-link">💰 BAKİYE</a>
            {% if user.role == 'ADMIN' %}<a href="/?p=ADMIN" class="nav-link">⚙️ PANEL</a>{% endif %}
            <a href="/logout" class="nav-link" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <div id="modal">
        <div class="slot-content" id="m-bg">
            <h2 id="m-title">Oyun</h2>
            <div class="reels">
                <div id="r1" class="reel">💎</div><div id="r2" class="reel">💎</div><div id="r3" class="reel">💎</div>
            </div>
            <p id="m-win" style="color:#fcd535; font-weight:bold; height:20px;"></p>
            <button id="s-btn" class="btn" onclick="spinNow()">SPIN (10 €)</button><br><br>
            <button onclick="location.reload()" style="background:none; border:none; color:#aaa; text-decoration:underline;">Lobiye Dön</button>
        </div>
    </div>

    <script>
    let activeGame = "";
    function openSlot(n){
        activeGame = n; document.getElementById('m-title').innerText = n;
        document.getElementById('modal').style.display = 'flex';
        fetch('/theme?n='+n).then(r=>r.json()).then(d=> document.getElementById('m-bg').style.background = d.bg);
    }
    async function spinNow(){
        let res = await fetch('/spin', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'game='+activeGame});
        let d = await res.json();
        if(d.err){ alert(d.err); return; }
        document.getElementById('s-btn').disabled = true;
        let i = 0;
        let t = setInterval(()=>{
            document.getElementById('r1').innerText = d.pool[Math.floor(Math.random()*d.pool.length)];
            document.getElementById('r2').innerText = d.pool[Math.floor(Math.random()*d.pool.length)];
            document.getElementById('r3').innerText = d.pool[Math.floor(Math.random()*d.pool.length)];
            if(i++ > 12){
                clearInterval(t);
                document.getElementById('r1').innerText = d.res[0];
                document.getElementById('r2').innerText = d.res[1];
                document.getElementById('r3').innerText = d.res[2];
                document.getElementById('main-bal').innerText = d.nb + " €";
                document.getElementById('s-btn').disabled = false;
                if(d.win > 0) {
                    document.getElementById('m-win').innerText = d.msg;
                    confetti({ particleCount: 200, spread: 80, origin: { y: 0.6 } });
                }
            }
        }, 80);
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    user_data = db["users"].get(u, {"bakiye": 0, "role": "USER"})
    return render_template_string(HTML, db=db, user=user_data, oyunlar=OYUNLAR, p=request.args.get('p'), session=session)

@app.route('/login', methods=['POST'])
def login():
    u, p, act = request.form.get('u'), request.form.get('p'), request.form.get('act')
    if act == "in":
        if u in db["users"] and db["users"][u]["pw"] == p: session["user"] = u
    else:
        db["basvurular"].append({"u": u, "p": p})
    return redirect('/')

@app.route('/admin/onay/<int:id>')
def admin_onay(id):
    if session.get("user") == "admin":
        b = db["basvurular"].pop(id)
        db["users"][b['u']] = {"pw": b['p'], "ad": b['u'], "role": "USER", "bakiye": 0.0}
    return redirect('/?p=ADMIN')

@app.route('/talep', methods=['POST'])
def talep():
    u = session.get("user")
    if u: db["bakiye_talepleri"].append({"u": u, "amt": float(request.form.get('amt'))})
    return redirect('/')

@app.route('/admin/bakiye/<int:id>')
def admin_bakiye(id):
    if session.get("user") == "admin":
        t = db["bakiye_talepleri"].pop(id)
        if t['u'] in db["users"]: db["users"][t['u']]["bakiye"] += t['amt']
    return redirect('/?p=ADMIN')

@app.route('/theme')
def theme(): return jsonify(OYUN_DATA.get(request.args.get('n'), {"bg": "#1c1f26"}))

@app.route('/spin', methods=['POST'])
def spin():
    u = session.get("user")
    if not u: return jsonify({"err": "Giriş yap!"})
    game = request.form.get('game')
    bet = 10.0
    if db["users"][u]["bakiye"] < bet: return jsonify({"err": "Bakiye bitti!"})
    db["users"][u]["bakiye"] -= bet
    data = OYUN_DATA[game]
    is_win = random.random() < 0.22 
    if is_win:
        s = random.choice(data["s"])
        res = [s, s, s]; win_amt = bet * random.randint(5, 20)
        db["users"][u]["bakiye"] += win_amt
    else:
        res = random.sample(data["s"], 3); win_amt = 0
    return jsonify({"res": res, "win": win_amt, "nb": db["users"][u]["bakiye"], "msg": data["win_text"], "pool": data["s"]})

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
