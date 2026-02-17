import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_pro_bet_system"

# --- VERİ TABANI (Üyeler ve Bakiyeler Burada Tutulur) ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}},
}

# --- SVG SEMBOLLER ---
SYMBOLS = {
    "red_heart": '<svg viewBox="0 0 100 100"><path d="M50 85l-5-5C20 55 5 40 5 25 5 15 13 7 23 7c6 0 12 3 16 8 4-5 10-8 16-8 10 0 18 8 18 18 0 15-15 30-40 55l-3 3z" fill="#ff004c"/></svg>',
    "purple_square": '<svg viewBox="0 0 100 100"><rect x="15" y="15" width="70" height="70" rx="15" fill="#a020f0"/></svg>',
    "green_diamond": '<svg viewBox="0 0 100 100"><path d="M50 10L10 50L50 90L90 50Z" fill="#00ff00"/></svg>',
    "blue_oval": '<svg viewBox="0 0 100 100"><ellipse cx="50" cy="50" rx="40" ry="30" fill="#0000ff"/></svg>',
    "yellow_banana": '<svg viewBox="0 0 100 100"><path d="M20 20C40 20 80 40 80 80C60 80 20 60 20 20" fill="#ffe135"/></svg>',
    "orange_circle": '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="35" fill="#ffa500"/></svg>',
    "pink_candy": '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="30" fill="#ff69b4"/></svg>',
    "lollipop": '<svg viewBox="0 0 100 100"><circle cx="50" cy="40" r="30" fill="url(#grad)"/><rect x="45" y="70" width="10" height="25" fill="#fff"/><defs><radialGradient id="grad"><stop offset="10%" stop-color="white"/><stop offset="100%" stop-color="#ff0080"/></radialGradient></defs></svg>'
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; }
        .header { background:#fcd535; color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:rgba(22, 24, 28, 0.9); margin:10px; padding:20px; border-radius:15px; border:1px solid #333; text-align:center; }
        
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; z-index:1000; background:rgba(0,0,0,0.9); flex-direction:column; align-items:center; justify-content:center; }
        .slot-content { 
            width:95%; max-width:480px; padding:15px; border-radius:25px; border:4px solid #fcd535; text-align:center;
            background: linear-gradient(-45deg, #ff75bd, #7001bb); background-size: 400% 400%;
        }
        .reels-grid { display:grid; grid-template-columns: repeat(6, 1fr); gap:4px; margin:10px auto; background:rgba(0,0,0,0.4); padding:8px; border-radius:12px; }
        .cell { width:100%; aspect-ratio: 1/1; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.05); border-radius:5px; }
        .cell svg { width:85%; height:85%; }
        
        /* Bahis Kontrol Paneli */
        .bet-control { display:flex; align-items:center; justify-content:center; gap:15px; margin:15px 0; background:rgba(0,0,0,0.5); padding:10px; border-radius:50px; }
        .bet-btn { background:#fcd535; color:black; border:none; width:40px; height:40px; border-radius:50%; font-size:20px; font-weight:bold; cursor:pointer; }
        .bet-display { font-size:20px; font-weight:bold; min-width:60px; }

        .btn-spin { background:#fcd535; color:black; border:none; padding:18px; border-radius:50px; font-weight:bold; width:100%; font-size:1.2rem; cursor:pointer; box-shadow:0 4px 0 #b39700; }
        .btn-spin:active { transform:translateY(2px); box-shadow:none; }
    </style>
</head>
<body>
    <div class="header">💎 CASINO7-24 PRESTIGE</div>

    {% if not session.user %}
        <div class="card">
            <h3>ÜYE GİRİŞİ</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı Adı" required style="width:80%; padding:12px; margin:5px; background:#111; color:white; border:1px solid #444;"><br>
                <button class="btn-spin" style="width:85%; margin-top:10px;">GİRİŞ YAP</button>
            </form>
        </div>
    {% else %}
        <div class="card">
            <span style="color:#aaa;">HOŞ GELDİN, {{ session.user }}</span><br>
            <b id="lobby-bal" style="color:#0ecb81; font-size:28px;">{{ user.bakiye }} €</b>
        </div>

        <div style="padding:10px;">
            <div onclick="openGame()" style="background:linear-gradient(45deg, #ff75bd, #ff0080); border-radius:20px; padding:40px; text-align:center; cursor:pointer; border:3px solid #fcd535;">
                <h1 style="margin:0; text-shadow:2px 2px 0 #000;">SWEET BONANZA</h1>
                <p>Oynamak İçin Dokun</p>
            </div>
        </div>

        <div class="card" style="font-size:13px;">
            <div style="border-bottom:1px solid #444; padding-bottom:10px; margin-bottom:10px; font-weight:bold;">AKTİF ÜYELER VE BAKİYELERİ</div>
            {% for name, d in db_users.items() %}
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #222;">
                <span>{{ name }}</span>
                <b style="color:#0ecb81;">{{ d.bakiye }} €</b>
            </div>
            {% endfor %}
        </div>
    {% endif %}

    <div id="modal">
        <div class="slot-content">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:white; font-weight:bold;">
                <span>Sweet Bonanza</span>
                <span id="m-bal">{{ user.bakiye }} €</span>
            </div>
            
            <div class="reels-grid" id="reels-box"></div>
            <div id="m-msg" style="height:25px; color:#fff; font-weight:bold; margin-bottom:10px;"></div>

            <div class="bet-control">
                <button class="bet-btn" onclick="changeBet(-1)">▼</button>
                <div class="bet-display"><span id="bet-val">1</span> €</div>
                <button class="bet-btn" onclick="changeBet(1)">▲</button>
            </div>

            <button id="s-btn" class="btn-spin" onclick="spinNow()">SPIN ÇEVİR</button>
            <button onclick="document.getElementById('modal').style.display='none'" style="background:none; border:none; color:#ddd; margin-top:15px; text-decoration:underline; cursor:pointer;">LOBİYE DÖN</button>
        </div>
    </div>

    <script>
    const SYMBOLS = {{ SYMBOLS|tojson }};
    let currentBet = 1;

    function changeBet(val) {
        let newVal = currentBet + val;
        if(newVal >= 1 && newVal <= 10) {
            currentBet = newVal;
            document.getElementById('bet-val').innerText = currentBet;
        }
    }

    function openGame(){
        document.getElementById('modal').style.display = 'flex';
        let box = document.getElementById('reels-box');
        box.innerHTML = "";
        for(let i=0; i<30; i++) box.innerHTML += `<div id="c${i}" class="cell">${SYMBOLS.red_heart}</div>`;
    }

    async function spinNow(){
        const btn = document.getElementById('s-btn');
        btn.disabled = true;
        
        let res = await fetch('/spin', {
            method:'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `bet=${currentBet}`
        });
        let d = await res.json();
        
        if(d.err) { alert(d.err); btn.disabled = false; return; }

        let frames = 0;
        let timer = setInterval(()=>{
            for(let j=0; j<30; j++){
                let keys = Object.keys(SYMBOLS);
                document.getElementById('c'+j).innerHTML = SYMBOLS[keys[Math.floor(Math.random()*keys.length)]];
            }
            if(frames++ > 10){
                clearInterval(timer);
                d.res.forEach((s, i) => { document.getElementById('c'+i).innerHTML = SYMBOLS[s]; });
                
                document.getElementById('m-bal').innerText = d.nb + " €";
                document.getElementById('lobby-bal').innerText = d.nb + " €";
                
                if(d.win > 0){
                    document.getElementById('m-msg').innerText = "KAZANDIN: " + d.win + " €";
                    confetti({ particleCount: 150, spread: 60 });
                } else {
                    document.getElementById('m-msg').innerText = "";
                }
                btn.disabled = false;
            }
        }, 70);
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    user_data = db["users"].get(u, {"bakiye": 0})
    return render_template_string(HTML, db_users=db["users"], user=user_data, SYMBOLS=SYMBOLS)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]:
        db["users"][u] = {"pw": "123", "bakiye": 100.0} # Yeni üye başlangıç bakiyesi
    return redirect('/')

@app.route('/spin', methods=['POST'])
def spin():
    u = session.get("user")
    bet = int(request.form.get('bet', 1))
    
    if db["users"][u]["bakiye"] < bet: 
        return jsonify({"err": "Bakiye yetersiz!"})
    
    db["users"][u]["bakiye"] -= bet
    
    keys = list(SYMBOLS.keys())
    res = [random.choice(keys) for _ in range(30)]
    
    counts = {}
    for s in res: counts[s] = counts.get(s, 0) + 1
    
    win_amt = 0
    # Kasa koruması: %10 kazanma şansı
    if random.random() < 0.10:
        for s, count in counts.items():
            if count >= 8:
                win_amt = bet * random.randint(5, 20)
                db["users"][u]["bakiye"] += win_amt
                break

    return jsonify({"res": res, "win": win_amt, "nb": db["users"][u]["bakiye"]})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
