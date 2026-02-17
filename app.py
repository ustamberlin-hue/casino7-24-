import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_sweet_bonanza_beta"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}},
    "basvurular": [],
    "bakiye_talepleri": []
}

# --- SWEET BONANZA İÇİN GERÇEK SEMBOLLER VE AYARLAR ---
# Sweet Bonanza'nın 6x5 ızgarasına uygun hale getirilmiştir.
# Her sembol için direkt görsel linki kullanılmıştır.
OYUN_DATA = {
    "Sweet Bonanza": {
        "s": [
            "https://i.imgur.com/K5m5h7G.png", # Kırmızı Kalp Şeker
            "https://i.imgur.com/X0S3B7r.png", # Mor Kare Şeker
            "https://i.imgur.com/G4P4Q2U.png", # Yeşil Elmas Şeker
            "https://i.imgur.com/H1J1p1x.png", # Mavi Oval Şeker
            "https://i.imgur.com/L7E7k7u.png", # Elma
            "https://i.imgur.com/P2N2o2y.png", # Erik
            "https://i.imgur.com/R3S3p3t.png", # Karpuz
            "https://i.imgur.com/T4U4v4w.png"  # Muz
        ],
        "rows": 5, "cols": 6, # 6x5 Izgara = 30 sembol
        "c1": "#ff75bd", "c2": "#ffafbd", # Arka plan renkleri
        "win_text": "🍬 BÜYÜK KAZANÇ!"
    }
}

OYUNLAR = [
    {"ad": "Sweet Bonanza", "img": "https://i.imgur.com/s6n5o5k.png"}, # Sweet Bonanza logosu
    # Diğer oyunlar şimdilik yok, sadece Sweet Bonanza odaklıyız
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
            width:95%; max-width:550px; padding:20px; border-radius:30px; border:4px solid #fcd535; text-align:center;
            background-size: 400% 400%; animation: flow 10s ease infinite; box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }
        .reels-grid { 
            display:grid; 
            grid-template-columns: repeat(var(--cols), 1fr); 
            gap:5px; 
            margin:20px auto;
            width:fit-content; /* Izgaranın ortalanması için */
            background:rgba(0,0,0,0.6);
            padding:10px;
            border-radius:15px;
            border:1px solid rgba(255,255,255,0.1);
        }
        .reel-cell { 
            width:60px; height:60px; 
            display:flex; align-items:center; justify-content:center; 
            font-size:30px; 
            border-radius:8px; 
            overflow:hidden;
            transition: transform 0.2s ease-out, opacity 0.2s ease-out;
        }
        .reel-cell img { width:100%; height:100%; object-fit:contain; }
        
        .btn-spin { background:#fcd535; color:black; border:none; padding:15px; border-radius:50px; font-weight:bold; width:100%; font-size:1.1rem; cursor:pointer; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; z-index:100; }
        .nav-item { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:11px; }
    </style>
</head>
<body id="body-bg">
    <div class="header">🎰 CASINO7-24 PROTOTYPE</div>

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
            <div class="reels-grid" id="reels-box" style="--cols:6;"></div>
            <p id="m-msg" style="height:25px; color:#fcd535; font-weight:bold; font-size:1.2rem; text-shadow: 0 0 10px black;"></p>
            <button id="s-btn" class="btn-spin" onclick="spinNow()">SPIN ÇEVİR (10€)</button>
            <button onclick="location.reload()" style="background:none; border:none; color:white; margin-top:20px; text-decoration:underline;">KAPAT</button>
        </div>
    </div>

    <script>
    let activeGame = "";
    let gameSettings = {};

    function openGame(n){
        activeGame = n;
        document.getElementById('m-title').innerText = n;
        document.getElementById('modal').style.display = 'flex';
        fetch('/theme?n='+n).then(r=>r.json()).then(d=>{
            gameSettings = d; // Oyun ayarlarını kaydet
            document.getElementById('m-bg').style.backgroundImage = `linear-gradient(-45deg, ${d.c1}, ${d.c2}, ${d.c1}, ${d.c2})`;
            document.getElementById('body-bg').style.background = d.c1;
            
            let box = document.getElementById('reels-box');
            box.style.setProperty('--cols', d.cols); // CSS grid sütun sayısını ayarla
            box.innerHTML = "";
            for(let i=0; i < d.rows * d.cols; i++){
                box.innerHTML += `<div id="r${i}" class="reel-cell"><img src="${d.s[0]}"></div>`; // Başlangıç sembolü
            }
        });
    }

    async function spinNow(){
        let res = await fetch('/spin', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'game='+activeGame});
        let d = await res.json();
        if(d.err){ alert(d.err); return; }
        
        document.getElementById('s-btn').disabled = true;
        document.getElementById('m-msg').innerText = "";
        
        let totalCells = gameSettings.rows * gameSettings.cols;
        let frames = 0;
        let timer = setInterval(()=>{
            for(let j=0; j < totalCells; j++){
                // Rastgele döner sembolleri göster
                let randomSymbol = gameSettings.s[Math.floor(Math.random()*gameSettings.s.length)];
                document.getElementById('r'+j).innerHTML = `<img src="${randomSymbol}">`;
            }
            if(frames++ > 15){ // Spin süresi
                clearInterval(timer);
                for(let j=0; j < totalCells; j++){ 
                    document.getElementById('r'+j).innerHTML = `<img src="${d.res[j]}">`;
                }
                document.getElementById('m-bal').innerText = d.nb + " €";
                
                if(d.win > 0) {
                    document.getElementById('m-msg').innerText = d.msg;
                    confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
                    // Basit bir "patlama" efekti simülasyonu
                    setTimeout(()=>{
                        for(let j=0; j < totalCells; j++){
                            if(d.winning_cells && d.winning_cells.includes(j)){
                                let cell = document.getElementById('r'+j);
                                cell.style.transform = 'scale(0)';
                                cell.style.opacity = '0';
                            }
                        }
                        setTimeout(()=>{
                             // Kazanan sembolleri kaldır ve yenilerini getir
                            fetch('/spin', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'game='+activeGame+'&respin=true'})
                            .then(r=>r.json())
                            .then(new_d => {
                                for(let j=0; j < totalCells; j++){
                                    let cell = document.getElementById('r'+j);
                                    cell.style.transform = 'scale(1)';
                                cell.style.opacity = '1';
                                    cell.innerHTML = `<img src="${new_d.res[j]}">`;
                                }
                                document.getElementById('m-bal').innerText = new_d.nb + " €";
                                if(new_d.win > 0) {
                                     document.getElementById('m-msg').innerText = new_d.msg + " (Respin!)";
                                } else {
                                     document.getElementById('m-msg').innerText = "";
                                }
                                document.getElementById('s-btn').disabled = false;
                            });
                        }, 500); // Semboller kaybolduktan sonra yeni semboller düşer
                    }, 1000); // Patlama animasyonu süresi
                } else {
                    document.getElementById('s-btn').disabled = false;
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
    is_respin = request.form.get('respin') == 'true'

    if not is_respin and db["users"][u]["bakiye"] < bet: return jsonify({"err": "Bakiye bitti!"})
    if not is_respin: db["users"][u]["bakiye"] -= bet
    
    data = OYUN_DATA[game]
    total_cells = data["rows"] * data["cols"]
    
    # Kazanma mantığı (Basitçe 8 aynı sembolü yakalamak)
    # Sweet Bonanza'da "pay anywhere" olduğu için 8+ aynı sembol aranır.
    is_win = random.random() < 0.25 # %25 Kazanma Şansı
    
    final_reels = []
    winning_cells = []
    win_amt = 0

    if is_win:
        # Rastgele 8-15 arası aynı sembol üret
        winning_symbol = random.choice(data["s"])
        num_winning_symbols = random.randint(8, 15)
        
        # Tüm hücrelere rastgele sembolleri doldur
        for _ in range(total_cells):
            final_reels.append(random.choice(data["s"]))

        # Kazanan sembolleri rastgele hücrelere yerleştir
        for _ in range(num_winning_symbols):
            idx = random.randint(0, total_cells - 1)
            final_reels[idx] = winning_symbol
            winning_cells.append(idx)
        
        win_amt = bet * random.choice([2, 5, 10, 20])
        db["users"][u]["bakiye"] += win_amt
    else:
        # Kazanma yoksa tamamen rastgele semboller
        for _ in range(total_cells):
            final_reels.append(random.choice(data["s"]))
        win_amt = 0
        
    return jsonify({
        "res": final_reels, 
        "win": win_amt, 
        "nb": db["users"][u]["bakiye"], 
        "msg": data["win_text"], 
        "pool": data["s"], 
        "cols": data["cols"],
        "winning_cells": winning_cells # Kazanan hücreleri işaretlemek için
    })

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
