import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_svg_edition"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}},
    "basvurular": [],
    "bakiye_talepleri": []
}

# --- OYUN AYARLARI ---
# Semboller SVG (kod) olarak tanımlandı, asla kırılmaz!
SYMBOLS = {
    "red_heart": '<svg viewBox="0 0 100 100"><path d="M50 85l-5-5C20 55 5 40 5 25 5 15 13 7 23 7c6 0 12 3 16 8 4-5 10-8 16-8 10 0 18 8 18 18 0 15-15 30-40 55l-3 3z" fill="#ff004c"/></svg>',
    "purple_square": '<svg viewBox="0 0 100 100"><rect x="15" y="15" width="70" height="70" rx="15" fill="#a020f0"/></svg>',
    "green_diamond": '<svg viewBox="0 0 100 100"><path d="M50 10L10 50L50 90L90 50Z" fill="#00ff00"/></svg>',
    "blue_oval": '<svg viewBox="0 0 100 100"><ellipse cx="50" cy="50" rx="40" ry="30" fill="#0000ff"/></svg>',
    "yellow_banana": '<svg viewBox="0 0 100 100"><path d="M20 20C40 20 80 40 80 80C60 80 20 60 20 20" fill="#ffe135"/></svg>',
    "lollipop": '<svg viewBox="0 0 100 100"><circle cx="50" cy="40" r="30" fill="url(#grad)"/><rect x="45" y="70" width="10" height="25" fill="#fff"/><defs><radialGradient id="grad"><stop offset="10%" stop-color="white"/><stop offset="100%" stop-color="#ff0080"/></radialGradient></defs></svg>'
}

OYUN_DATA = {
    "Sweet Bonanza": {
        "s": list(SYMBOLS.keys()),
        "rows": 5, "cols": 6,
        "c1": "#ff75bd", "c2": "#ffafbd"
    }
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        @keyframes flow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; }
        .header { background:#fcd535; color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:rgba(22, 24, 28, 0.9); margin:10px; padding:15px; border-radius:12px; border:1px solid #333; }
        
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
        .slot-content { 
            width:95%; max-width:500px; padding:15px; border-radius:30px; border:4px solid #fcd535; text-align:center;
            background-size: 400% 400%; animation: flow 10s ease infinite; 
        }
        .reels-grid { 
            display:grid; grid-template-columns: repeat(6, 1fr); gap:5px; 
            margin:15px auto; background:rgba(0,0,0,0.5); padding:10px; border-radius:15px;
        }
        .cell { 
            width:100%; aspect-ratio: 1/1; display:flex; align-items:center; justify-content:center; 
            background:rgba(255,255,255,0.1); border-radius:8px; transition: 0.3s;
        }
        .cell svg { width:80%; height:80%; filter: drop-shadow(0 0 5px rgba(255,255,255,0.3)); }
        .pop { transform: scale(0); opacity: 0; }
        
        .btn-spin { background:#fcd535; color:black; border:none; padding:18px; border-radius:50px; font-weight:bold; width:100%; font-size:1.2rem; cursor:pointer; box-shadow: 0 5px 0 #b39700; }
        .btn-spin:active { transform: translateY(3px); box-shadow: none; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; }
        .nav-item { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:11px; }
    </style>
</head>
<body id="body-bg">
    <div class="header">💎 CASINO7-24 VIP</div>

    {% if not session.user %}
        <div style="padding:40px; text-align:center;">
            <h3>OTURUM AÇ</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı Adı" required style="width:90%; padding:15px; margin:10px; background:#1c1f26; color:white; border:1px solid #444;">
                <input type="password" name="p" placeholder="Şifre" required style="width:90%; padding:15px; margin:10px; background:#1c1f26; color:white; border:1px solid #444;">
                <button name="act" value="in" class="btn-spin">GİRİŞ YAP</button>
            </form>
        </div>
    {% else %}
        <div class="card" style="text-align:center;">
            <span style="color:#aaa;">BAKİYENİZ</span><br>
            <b style="color:#0ecb81; font-size:32px;">{{ user.bakiye }} €</b>
        </div>

        <div style="padding:10px;">
            <div onclick="openGame('Sweet Bonanza')" style="background:linear-gradient(45deg, #ff75bd, #ffafbd); border-radius:20px; padding:30px; text-align:center; cursor:pointer; border:3px solid #fcd535;">
                <h1 style="margin:0; text-shadow: 2px 2px 0 #ff0080;">SWEET BONANZA</h1>
                <p>6x5 GRID • TUMBLE WIN</p>
            </div>
        </div>

        <div class="card" style="font-size:12px;">
            <center><b>CANLI LİSTE</b></center>
            {% for name, d in db.users.items() %}
            <div style="display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #222;">
                <span>{{ name }}</span><b>{{ d.bakiye }} €</b>
            </div>
            {% endfor %}
        </div>

        <div class="nav">
            <a href="/" class="nav-item">🎰 OYUNLAR</a>
            <a href="/logout" class="nav-item" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <div id="modal">
        <div class="slot-content" id="m-bg">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; background:rgba(0,0,0,0.6); padding:10px; border-radius:15px;">
                <span id="m-title">Sweet Bonanza</span>
                <span id="m-bal" style="color:#0ecb81; font-weight:bold;">{{ user.bakiye }} €</span>
            </div>
            <div class="reels-grid" id="reels-box"></div>
            <div id="m-msg" style="height:30px; color:#fcd535; font-weight:bold; font-size:1.3rem;"></div>
            <button id="s-btn" class="btn-spin" onclick="spinNow()">SPIN (10€)</button>
            <button onclick="location.reload()" style="background:none; border:none; color:white; margin-top:15px; text-decoration:underline;">LOBİYE DÖN</button>
        </div>
    </div>

    <script>
    const SYMBOLS = {{ SYMBOLS|tojson }};
    let activeGame = "Sweet Bonanza";

    function openGame(n){
        document.getElementById('modal').style.display = 'flex';
        fetch('/theme?n='+n).then(r=>r.json()).then(d=>{
            document.getElementById('m-bg').style.backgroundImage = `linear-gradient(-45deg, ${d.c1}, ${d.c2}, ${d.c1}, ${d.c2})`;
            let box = document.getElementById('reels-box');
            box.innerHTML = "";
            for(let i=0; i<30; i++) box.innerHTML += `<div id="c${i}" class="cell">${SYMBOLS.red_heart}</div>`;
        });
    }

    async function spinNow(){
        document.getElementById('s-btn').disabled = true;
        let res = await fetch('/spin', {method:'POST'});
        let d = await res.json();
        if(d.err) { alert(d.err); return; }

        let frames = 0;
        let timer = setInterval(()=>{
            for(let j=0; j<30; j++){
                let keys = Object.keys(SYMBOLS);
                document.getElementById('c'+j).innerHTML = SYMBOLS[keys[Math.floor(Math.random()*keys.length)]];
            }
            if(frames++ > 12){
                clearInterval(timer);
                d.res.forEach((s, i) => document.getElementById('c'+i).innerHTML = SYMBOLS[s]);
                document.getElementById('m-bal').innerText = d.nb + " €";
                
                if(d.win > 0){
                    confetti({ particleCount: 200, spread: 70, origin: { y: 0.6 } });
                    document.getElementById('m-msg').innerText = "KAZANDIN: " + d.win + " €";
                    // Patlama Efekti
                    setTimeout(()=>{
                        d.wins.forEach(idx => document.getElementById('c'+idx).classList.add('pop'));
                        setTimeout(()=> {
                             location.reload(); // Bakiyeyi güncellemek için
                        }, 800);
                    }, 1000);
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
    return render_template_string(HTML, db=db, user=user_data, SYMBOLS=SYMBOLS, session=session)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    if u in db["users"]: session["user"] = u
    return redirect('/')

@app.route('/theme')
def theme(): return jsonify(OYUN_DATA["Sweet Bonanza"])

@app.route('/spin', methods=['POST'])
def spin():
    u = session.get("user")
    if db["users"][u]["bakiye"] < 10: return jsonify({"err": "Bakiye bitti!"})
    db["users"][u]["bakiye"] -= 10
    
    # 6x5 Izgara üretimi
    res = [random.choice(list(SYMBOLS.keys())) for _ in range(30)]
    
    # Kazanma kontrolü (8+ aynı sembol)
    counts = {}
    for s in res: counts[s] = counts.get(s, 0) + 1
    
    win_amt = 0
    winning_indices = []
    for s, count in counts.items():
        if count >= 8:
            win_amt += 10 * count
            winning_indices = [i for i, x in enumerate(res) if x == s]
            
    db["users"][u]["bakiye"] += win_amt
    return jsonify({"res": res, "win": win_amt, "nb": db["users"][u]["bakiye"], "wins": winning_indices})

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
