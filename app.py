import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_animated_v1"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}},
    "basvurular": [],
    "bakiye_talepleri": []
}

# --- OYUN DATA (Hareketli Renk Paletleri Eklendi) ---
OYUN_DATA = {
    "Sweet Bonanza": {"s": ["🍭", "🍉", "🍎", "🍇", "🍌", "🍬"], "cols": 4, "c1": "#ff75bd", "c2": "#ffafbd", "win_text": "🍭 ŞEKER PATLAMASI!"},
    "Gates of Olympus": {"s": ["⚡", "👑", "💍", "🍷", "💎", "🔱"], "cols": 5, "c1": "#4b0082", "c2": "#000000", "win_text": "⚡ ZEUS ÇARPTI!"},
    "The Dog House": {"s": ["🐶", "🦴", "🏠", "🐕", "🐾"], "cols": 3, "c1": "#8b4513", "c2": "#deb887", "win_text": "🐾 HAV HAV KAZANÇ!"},
    "Big Bass Bonanza": {"s": ["🐟", "🎣", "🛶", "🛟", "🐠"], "cols": 4, "c1": "#0077be", "c2": "#00a8cc", "win_text": "🎣 BÜYÜK BALIK!"},
    "Sugar Rush": {"s": ["🧸", "🍬", "🧁", "🍩", "🍭"], "cols": 5, "c1": "#db7093", "c2": "#ffc0cb", "win_text": "🧸 REÇEL DOLU!"},
    "Wanted Dead or Wild": {"s": ["🤠", "🔫", "🥃", "🌵", "💰"], "cols": 3, "c1": "#3d2b1f", "c2": "#1a1a1a", "win_text": "🔫 DÜELLO!"},
    "Starlight Princess": {"s": ["⭐", "💖", "🌙", "👑", "🔮"], "cols": 4, "c1": "#1e90ff", "c2": "#00008b", "win_text": "⭐ YILDIZ GÜCÜ!"},
    "Wolf Gold": {"s": ["🐺", "🌙", "🦅", "🐂", "🐎"], "cols": 3, "c1": "#2f4f4f", "c2": "#000000", "win_text": "🐺 ULUMA BONUSU!"}
}

OYUNLAR = [
    {"ad": "Sweet Bonanza", "img": "https://img.freepik.com/premium-photo/colorful-candies-sweets-falling-into-slot-machine-generative-ai_175880-1430.jpg"},
    {"ad": "Gates of Olympus", "img": "https://img.freepik.com/free-photo/god-zeus-concept-illustration_23-2150534293.jpg"},
    {"ad": "The Dog House", "img": "https://img.freepik.com/free-photo/cute-puppy-house-concept_23-2150166254.jpg"},
    {"ad": "Big Bass Bonanza", "img": "https://img.freepik.com/premium-photo/fishing-hobby-professional-equipment-generative-ai_175880-1500.jpg"},
    {"ad": "Sugar Rush", "img": "https://img.freepik.com/premium-photo/pink-candyland-abstract-background-generative-ai_175880-1200.jpg"},
    {"ad": "Wanted Dead or Wild", "img": "https://img.freepik.com/free-photo/wild-west-wanted-poster-vintage_23-2150166600.jpg"},
    {"ad": "Starlight Princess", "img": "https://img.freepik.com/premium-photo/anime-princess-starry-night-generative-ai_175880-1600.jpg"},
    {"ad": "Wolf Gold", "img": "https://img.freepik.com/free-photo/wolf-concept-illustration_23-2150166540.jpg"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        @keyframes flow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; transition: background 1s ease; }
        .header { background:#fcd535; color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:rgba(22, 24, 28, 0.8); margin:10px; padding:15px; border-radius:12px; border:1px solid #333; backdrop-filter: blur(5px); }
        .grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; padding:12px; }
        .game-card { background:#1c1f26; border-radius:15px; overflow:hidden; border:1px solid #444; cursor:pointer; }
        .game-card img { width:100%; height:130px; object-fit:cover; }
        
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
        .slot-content { 
            width:95%; max-width:450px; padding:20px; border-radius:30px; border:4px solid #fcd535; text-align:center;
            background-size: 400% 400%; animation: flow 10s ease infinite; box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }
        .reels-container { display:flex; justify-content:center; gap:8px; margin:20px 0; }
        .reel { background:rgba(0,0,0,0.7); width:65px; height:85px; display:flex; align-items:center; justify-content:center; font-size:40px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); }
        
        .btn-spin { background:#fcd535; color:black; border:none; padding:15px; border-radius:50px; font-weight:bold; width:100%; font-size:1.1rem; cursor:pointer; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; z-index:100; }
        .nav-item { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:11px; }
    </style>
</head>
<body id="body-bg">
    <div class="header">🎰 CASINO7-24 PRESTIGE</div>

    {% if not session.user %}
        <div style="padding:40px; text-align:center;">
            <h3>OTURUM AÇ</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı Adı" required style="width:90%; padding:15px; margin:10px; background:#1c1f26; color:white; border:1px solid #444;">
                <input type="password" name="p" placeholder="Şifre" required style="width:90%; padding:15px; margin:10px; background:#1c1f26; color:white; border:1px solid #444;">
                <button name="act" value="in" class="btn-spin">GİRİŞ</button>
                <button name="act" value="up" style="background:none; border:none; color:#aaa; margin-top:20px;">Kayıt Ol</button>
            </form>
        </div>
    {% else %}
        <div class="card" style="text-align:center;">
            <span style="color:#aaa;">BAKİYENİZ</span><br>
            <b style="color:#0ecb81; font-size:30px;">{{ user.bakiye }} €</b>
        </div>

        {% if p == 'ADMIN' %}
            <div style="padding:15px;"><h3>⚙️ PANEL</h3>
            {% for b in db.basvurular %}<div class="card">{{ b.u }} <a href="/admin/onay/{{loop.index0}}" style="color:lime;">[ONAY]</a></div>{% endfor %}
            {% for t in db.bakiye_talepleri %}<div class="card">{{ t.u }}: {{ t.amt }} € <a href="/admin/bakiye/{{loop.index0}}" style="color:lime;">[YÜKLE]</a></div>{% endfor %}
            </div>
        {% elif p == 'CASH' %}
            <div style="padding:40px; text-align:center;">
                <h3>💰 PARA YÜKLE</h3>
                <form action="/talep" method="post"><input type="number" name="amt" placeholder="Miktar" required style="width:100%; padding:15px; background:black; color:white;">
                <button class="btn-spin" style="margin-top:20px;">TALEP ET</button></form>
            </div>
        {% else %}
            <div class="grid">
                {% for g in oyunlar %}
                <div class="game-card" onclick="openGame('{{ g.ad }}')">
                    <img src="{{ g.img }}"><div style="padding:8px; text-align:center; font-weight:bold;">{{ g.ad }}</div>
                </div>
                {% endfor %}
            </div>
            <div class="card" style="font-size:12px;">
                <center><b>CANLI OYUNCULAR</b></center>
                {% for name, d in db.users.items() %}<div style="display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #222;"><span>{{ name }}</span><b>{{ d.bakiye }} €</b></div>{% endfor %}
            </div>
        {% endif %}

        <div class="nav">
            <a href="/" class="nav-item">🎰 OYUNLAR</a>
            <a href="/?p=CASH" class="nav-item">💰 KASA</a>
            {% if user.role == 'ADMIN' %}<a href="/?p=ADMIN" class="nav-item">⚙️ PANEL</a>{% endif %}
            <a href="/logout" class="nav-item" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <div id="modal">
        <div class="slot-content" id="m-bg">
            <div style="display:flex; justify-content:space-between; margin-bottom:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:10px;">
                <span id="m-title" style="font-weight:bold;">Oyun</span>
                <span id="m-bal" style="color:#0ecb81; font-weight:bold;">{{ user.bakiye }} €</span>
            </div>
            <div class="reels-container" id="reels-box"></div>
            <p id="m-msg" style="height:25px; color:#fcd535; font-weight:bold; font-size:1.2rem; text-shadow: 0 0 10px black;"></p>
            <button id="s-btn" class="btn-spin" onclick="spinNow()">SPIN ÇEVİR (10€)</button>
            <button onclick="location.reload()" style="background:none; border:none; color:white; margin-top:20px; text-decoration:underline;">KAPAT</button>
        </div>
    </div>

    <script>
    let activeGame = "";
    function openGame(n){
        activeGame = n;
        document.getElementById('m-title').innerText = n;
        document.getElementById('modal').style.display = 'flex';
        fetch('/theme?n='+n).then(r=>r.json()).then(d=>{
            // Hareketli Arka Plan Uygula
            document.getElementById('m-bg').style.backgroundImage = `linear-gradient(-45deg, ${d.c1}, ${d.c2}, ${d.c1}, ${d.c2})`;
            document.getElementById('body-bg').style.background = d.c1;
            
            let box = document.getElementById('reels-box');
            box.innerHTML = "";
            for(let i=0; i<d.cols; i++){
                box.innerHTML += `<div id="r${i}" class="reel">🎲</div>`;
            }
        });
    }

    async function spinNow(){
        let res = await fetch('/spin', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'game='+activeGame});
        let d = await res.json();
        if(d.err){ alert(d.err); return; }
        
        document.getElementById('s-btn').disabled = true;
        document.getElementById('m-msg').innerText = "";
        
        let frames = 0;
        let timer = setInterval(()=>{
            for(let j=0; j<d.cols; j++){
                document.getElementById('r'+j).innerText = d.pool[Math.floor(Math.random()*d.pool.length)];
            }
            if(frames++ > 15){
                clearInterval(timer);
                for(let j=0; j<d.cols; j++){ document.getElementById('r'+j).innerText = d.res[j]; }
                document.getElementById('m-bal').innerText = d.nb + " €";
                document.getElementById('s-btn').disabled = false;
                if(d.win > 0) {
                    document.getElementById('m-msg').innerText = d.msg;
                    confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
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
        db["users"][b['u']] = {"pw": b['p'], "ad": b['u'], "role": "USER", "bakiye": 100.0}
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
def theme(): return jsonify(OYUN_DATA.get(request.args.get('n')))

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
    cols = data["cols"]
    
    if is_win:
        s = random.choice(data["s"])
        res = [s] * cols
        win_amt = bet * random.randint(5, 30)
        db["users"][u]["bakiye"] += win_amt
    else:
        res = [random.choice(data["s"]) for _ in range(cols)]
        win_amt = 0
        
    return jsonify({"res": res, "win": win_amt, "nb": db["users"][u]["bakiye"], "msg": data["win_text"], "pool": data["s"], "cols": cols})

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
