import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "batak_vip_exclusive_2026"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "bakiye": 1000.0}},
}

BOT_ISIMLERI = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep", "Volkan", "Buse", "Emre", "Derya"]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; overflow:hidden; }
        .header { background:#111; padding:10px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fcd535; }
        
        .table-area { 
            position:relative; width:95vw; height:65vh; margin:10px auto; 
            background:radial-gradient(#155d27, #0a3316); border:10px solid #5d3a1a; border-radius:150px; 
            box-shadow: inset 0 0 50px #000;
        }
        
        .player { position:absolute; text-align:center; width:80px; }
        .p-top { top:10px; left:50%; transform:translateX(-50%); }
        .p-left { left:10px; top:50%; transform:translateY(-50%); }
        .p-right { right:10px; top:50%; transform:translateY(-50%); }
        .p-bottom { bottom:10px; left:50%; transform:translateX(-50%); }
        
        .avatar { width:60px; height:60px; background:#111; border:2px solid #fcd535; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:12px; }
        
        .cards-hand { position:fixed; bottom:20px; width:100%; display:flex; justify-content:center; gap:5px; padding:0 10px; box-sizing:border-box; }
        .card { 
            width:45px; height:70px; background:white; color:black; border-radius:5px; 
            border:1px solid #999; display:flex; flex-direction:column; align-items:center; justify-content:center;
            font-weight:bold; cursor:pointer; font-size:14px; transition:0.2s; position:relative;
        }
        .card:hover { transform:translateY(-15px); border:2px solid #fcd535; z-index:10; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }

        .bet-overlay { 
            position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); 
            display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:100;
        }
        .btn-gold { background:#fcd535; color:black; border:none; padding:15px 30px; border-radius:50px; font-weight:bold; cursor:pointer; font-size:1.1rem; text-decoration:none; display:inline-block; }
    </style>
</head>
<body>

    {% if not session.user %}
        <div class="bet-overlay">
            <h2 style="color:#fcd535">💎 CASINO BATAK VIP</h2>
            <form action="/login" method="post" style="text-align:center;">
                <input type="text" name="u" placeholder="Kullanıcı Adı" required style="padding:15px; border-radius:10px; border:none; width:200px;"><br><br>
                <button type="submit" class="btn-gold">MASAYA OTUR</button>
            </form>
        </div>
    {% else %}
        <div class="header">
            <span>👤 {{ session.user }}</span>
            <span style="color:#fcd535; font-weight:bold;">BAKİYE: {{ bakiye }} €</span>
            <a href="/logout" style="color:red; text-decoration:none; font-size:12px; font-weight:bold;">ÇIKIŞ</a>
        </div>

        {% if not session.get('in_game') %}
        <div class="bet-overlay">
            <h3 style="color:#fcd535">MASA ÜCRETİ: 20 €</h3>
            <p>Rakipleriniz {{ session.botlar|join(', ') }} masada bekliyor.</p>
            <a href="/start_game" class="btn-gold">BAHİSİ YATIR VE BAŞLA</a>
        </div>
        {% endif %}

        <div class="table-area">
            <div class="player p-top"><div class="avatar">{{ session.botlar[0] }}</div></div>
            <div class="player p-left"><div class="avatar">{{ session.botlar[1] }}</div></div>
            <div class="player p-right"><div class="avatar">{{ session.botlar[2] }}</div></div>
            <div class="player p-bottom"><div class="avatar">SİZ</div></div>
            
            <div id="table-center" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); display:flex; gap:10px;">
                <div style="border:2px dashed rgba(255,255,255,0.2); width:50px; height:75px; border-radius:5px;"></div>
                <div style="border:2px dashed rgba(255,255,255,0.2); width:50px; height:75px; border-radius:5px;"></div>
            </div>
        </div>

        <div class="cards-hand">
            {% for card in session.get('hand', []) %}
            <div class="card {{ card.type }}" onclick="alert('Sıra Bekleniyor...')">
                <span>{{ card.val }}</span>
                <span style="font-size:20px;">{{ card.symbol }}</span>
            </div>
            {% endfor %}
        </div>
    {% endif %}

</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    if not u:
        return render_template_string(HTML)
    
    # Kullanıcı verisini her seferinde güncel çek
    user_data = db["users"].get(u, {"bakiye": 0})
    return render_template_string(HTML, bakiye=user_data['bakiye'])

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]:
        db["users"][u] = {"pw": "123", "bakiye": 1000.0}
    
    session["botlar"] = random.sample(BOT_ISIMLERI, 3)
    session["in_game"] = False
    session["hand"] = []
    return redirect('/')

@app.route('/start_game')
def start_game():
    u = session.get("user")
    if not u or db["users"][u]["bakiye"] < 20:
        return "Bakiye Yetersiz! Lütfen sayfayı yenileyip tekrar deneyin."
    
    # Parayı düş
    db["users"][u]["bakiye"] -= 20
    session["in_game"] = True
    
    # Kartları Dağıt ve SIRALA
    tipler = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    degerler = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    
    new_hand = []
    # Rastgele 13 kart oluştur
    for _ in range(13):
        t = random.choice(tipler)
        new_hand.append({
            'type': t[0], 
            'symbol': t[1], 
            'val': random.choice(degerler)
        })
    
    session["hand"] = new_hand
    return redirect('/') # BURASI ÖNEMLİ: Oyunu başlatınca ana sayfaya dön!

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
