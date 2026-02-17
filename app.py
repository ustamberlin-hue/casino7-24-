import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_stable_v3"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "role": "ADMIN", "bakiye": 1000.0}},
}

# --- SVG SEMBOLLER (Çeşitlilik Artırıldı ki Sürekli Kazanmasın) ---
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
        .reels-grid { display:grid; grid-template-columns: repeat(6, 1fr); gap:4px; margin:15px auto; background:rgba(0,0,0,0.4); padding:8px; border-radius:12px; }
        .cell { width:100%; aspect-ratio: 1/1; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.05); border-radius:5px; transition: 0.3s; }
        .cell svg { width:85%; height:85%; }
        .pop { transform: scale(1.5); opacity: 0; transition: 0.5s; }
        
        .btn-spin { background:#fcd535; color:black; border:none; padding:18px; border-radius:50px; font-weight:bold; width:100%; font-size:1.2rem; cursor:pointer; }
        .btn-spin:disabled { background:#555; cursor:not-allowed; }
    </style>
</head>
<body>
    <div class="header">💎 CASINO7-24 PRO</div>

    {% if not session.user %}
        <div class="card">
            <h3>GİRİŞ YAP</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı Adı" required style="width:80%; padding:12px; margin:5px; background:#111; color:white; border:1px solid #444;"><br>
                <button class="btn-spin" style="width:85%; margin-top:10px;">GİRİŞ</button>
            </form>
        </div>
    {% else %}
        <div class="card">
            <span style="color:#aaa;">HOŞ GELDİN {{ session.user }}</span><br>
            <b id="lobby-bal" style="color:#0ecb81; font-size:28px;">{{ user.bakiye }} €</b>
        </div>

        <div style="padding:15px;">
            <div onclick="openGame()" style="background:linear-gradient(45deg, #ff75bd, #ff0080); border-radius:20px; padding:40px; text-align:center; cursor:pointer; border:3px solid #fcd535;">
                <h1 style="margin:0;">SWEET BONANZA</h1>
                <p>Oynamak İçin Dokun</p>
            </div>
        </div>
    {% endif %}

    <div id="modal">
        <div class="slot-content">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:white; font-weight:bold;">
                <span>Sweet Bonanza</span>
                <span id="m-bal">{{ user.bakiye }} €</span>
            </div>
            <div class="reels-grid" id="reels-box"></div>
            <div id="m-msg" style="height:30px; color:#fff; font-weight:bold; margin-bottom:5px;"></div>
            <button id="s-btn" class="btn-spin" onclick="spinNow()">SPIN (10€)</button>
            <button onclick="document.getElementById('modal').style.display='none'" style="background:none; border:none; color:#ddd; margin-top:15px; text-decoration:underline; cursor:pointer;">KAPAT</button>
        </div>
    </div>

    <script>
    const SYMBOLS = {{ SYMBOLS|tojson }};
    function openGame(){
        document.getElementById('modal').style.display = 'flex';
        let box = document.getElementById('reels-box');
        box.innerHTML = "";
        for(let i=0; i<30; i++) box.innerHTML += `<div id="c${i}" class="cell">${SYMBOLS.red_heart}</div>`;
    }

    async function spinNow(){
        const btn = document.getElementById('s-btn');
        btn.disabled = true;
        let res = await fetch('/spin', {method:'POST'});
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
                d.res.forEach((s, i) => {
                    const cell = document.getElementById('c'+i);
                    cell.innerHTML = SYMBOLS[s];
                    cell.classList.remove('pop');
                });
                
                document.getElementById('m-bal').innerText = d.nb + " €";
                document.getElementById('lobby-bal').innerText = d.nb + " €";
                
                if(d.win > 0){
                    document.getElementById('m-msg').innerText = "TEBRİKLER: " + d.win + " €";
                    confetti({ particleCount: 150, spread: 60 });
                    d.wins.forEach(idx => document.getElementById('c'+idx).classList.add('pop'));
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
    return render_template_string(HTML, db=db, user=user_data, SYMBOLS=SYMBOLS)

@app.route('/login', methods=['POST'])
def login():
    session["user"] = request.form.get('u')
    if session["user"] not in db["users"]:
        db["users"][session["user"]] = {"pw": "123", "bakiye": 1000.0}
    return redirect('/')

@app.route('/spin', methods=['POST'])
def spin():
    u = session.get("user")
    if db["users"][u]["bakiye"] < 10: return jsonify({"err": "Bakiye yetersiz!"})
    db["users"][u]["bakiye"] -= 10
    
    # Tüm sembol listesini al
    keys = list(SYMBOLS.keys())
    res = [random.choice(keys) for _ in range(30)]
    
    # Matematiksel Kontrol: Kazanma ihtimalini %15'e düşürdüm
    counts = {}
    for s in res: counts[s] = counts.get(s, 0) + 1
    
    win_amt = 0
    winning_indices = []
    
    # Gerçek Bonanza Kuralı: 8+ aynı sembol gelmeli
    for s, count in counts.items():
        if count >= 8: # Kazanma eşiği 8
            # Rastgele bir şans daha: Her 8+ yakaladığında kazanmasın (Kasa avantajı)
            if random.random() < 0.3: 
                win_amt += 10 * (count - 7) * 2 
                winning_indices = [i for i, x in enumerate(res) if x == s]
                break 

    db["users"][u]["bakiye"] += win_amt
    return jsonify({"res": res, "win": win_amt, "nb": db["users"][u]["bakiye"], "wins": winning_indices})

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
