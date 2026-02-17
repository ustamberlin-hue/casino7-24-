import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "batak_engine_v1"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "bakiye": 5000.0}},
}

BOT_NAMES = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep", "Volkan", "Buse"]

# --- KART MOTORU ---
def create_deck():
    suits = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    deck = []
    for s_name, s_sym in suits:
        for r in ranks:
            val = ranks.index(r) + 2
            deck.append({'suit': s_name, 'sym': s_sym, 'rank': r, 'val': val})
    random.shuffle(deck)
    return deck

def sort_hand(hand):
    # Türlere ve büyüklüğe göre sıralama (Batak standardı)
    order = {'spade': 4, 'heart': 3, 'diamond': 2, 'club': 1}
    return sorted(hand, key=lambda x: (order[x['suit']], x['val']), reverse=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; overflow:hidden; }
        .header { background:rgba(0,0,0,0.8); padding:10px; display:flex; justify-content:space-between; border-bottom:2px solid #fcd535; }
        
        .table { 
            position:relative; width:90vw; height:60vh; margin:40px auto; 
            background:radial-gradient(#1a7a35, #083316); border:12px solid #3d2611; border-radius:200px; 
            box-shadow: inset 0 0 100px #000;
        }
        
        .player { position:absolute; text-align:center; }
        .p0 { bottom:-40px; left:50%; transform:translateX(-50%); } /* SİZ */
        .p1 { left:-50px; top:50%; transform:translateY(-50%); }   /* BOT 1 */
        .p2 { top:-40px; left:50%; transform:translateX(-50%); }    /* BOT 2 */
        .p3 { right:-50px; top:50%; transform:translateY(-50%); }  /* BOT 3 */
        
        .avatar { width:70px; height:70px; background:#111; border:3px solid #fcd535; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; font-size:12px; }
        .bid-tag { background:#fcd535; color:black; font-weight:bold; padding:2px 8px; border-radius:10px; font-size:10px; margin-top:5px; }

        /* Kart Görselleri */
        .hand { position:fixed; bottom:15px; width:100%; display:flex; justify-content:center; padding-left:20px; }
        .card { 
            width:55px; height:85px; background:white; color:black; border-radius:6px; margin-left:-20px;
            border:1px solid #000; display:flex; flex-direction:column; align-items:center; justify-content:center;
            font-weight:bold; cursor:pointer; transition:0.2s; position:relative;
        }
        .card:hover { transform:translateY(-25px); z-index:100; border:2px solid #fcd535; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }

        .center-cards { position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); display:flex; gap:10px; }

        .overlay { 
            position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); 
            display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:1000;
        }
        .btn { background:#fcd535; color:black; border:none; padding:12px 25px; border-radius:50px; font-weight:bold; cursor:pointer; }
        .bid-btn { width:40px; height:40px; margin:5px; border-radius:50%; border:2px solid #fcd535; background:none; color:white; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>

    {% if not session.user %}
        <div class="overlay">
            <h2>💎 CASINO7-24 VIP BATAK</h2>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="İsim Yazın..." required style="padding:15px; border-radius:10px; width:200px;"><br><br>
                <button class="btn">MASAYA OTUR</button>
            </form>
        </div>
    {% elif not session.game_active %}
        <div class="overlay">
            <h3>MASA BAHİSİ SEÇİN</h3>
            <div style="margin:20px;">
                <button class="btn" onclick="location.href='/start/50'">50 €</button>
                <button class="btn" onclick="location.href='/start/100'">100 €</button>
                <button class="btn" onclick="location.href='/start/500'">500 €</button>
            </div>
            <p>Bakiyeniz: {{ user.bakiye }} €</p>
        </div>
    {% elif session.game_state == 'bidding' %}
        <div class="overlay">
            <h3>İHALE: KAÇ ALIRSIN?</h3>
            <div>
                {% for i in range(1, 14) %}
                <button class="bid-btn" onclick="location.href='/bid/{{i}}'">{{i}}</button>
                {% endfor %}
            </div>
        </div>
    {% endif %}

    <div class="header">
        <span>💰 Bakiye: <b>{{ user.bakiye }} €</b></span>
        <span>🃏 Bahis: <b style="color:#fcd535;">{{ session.current_bet }} €</b></span>
        <a href="/logout" style="color:red; font-size:12px;">Çıkış</a>
    </div>

    <div class="table">
        <div class="player p1"><div class="avatar"><span>{{ session.bots[0].name }}</span><div class="bid-tag">İhale: {{ session.bots[0].bid }}</div></div></div>
        <div class="player p2"><div class="avatar"><span>{{ session.bots[1].name }}</span><div class="bid-tag">İhale: {{ session.bots[1].bid }}</div></div></div>
        <div class="player p3"><div class="avatar"><span>{{ session.bots[2].name }}</span><div class="bid-tag">İhale: {{ session.bots[2].bid }}</div></div></div>
        <div class="player p0"><div class="avatar"><span>SİZ</span><div class="bid-tag">İhale: {{ session.my_bid }}</div></div></div>

        <div class="center-cards" id="arena">
            </div>
    </div>

    <div class="hand">
        {% for c in session.hand %}
        <div class="card {{ c.suit }}" onclick="playCard('{{loop.index0}}')">
            <div style="position:absolute; top:5px; left:5px;">{{ c.rank }}</div>
            <div style="font-size:25px;">{{ c.sym }}</div>
        </div>
        {% endfor %}
    </div>

    <script>
        function playCard(idx) {
            fetch('/play/' + idx).then(r => r.json()).then(data => {
                if(data.err) { alert(data.err); return; }
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    if not u: return render_template_string(HTML)
    user_data = db["users"].get(u, {"bakiye": 0})
    return render_template_string(HTML, user=user_data)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]: db["users"][u] = {"bakiye": 1000.0}
    session["game_active"] = False
    return redirect('/')

@app.route('/start/<int:bet>')
def start(bet):
    u = session.get("user")
    if db["users"][u]["bakiye"] < bet: return "Yetersiz Bakiye"
    
    db["users"][u]["bakiye"] -= bet
    session["current_bet"] = bet
    session["game_active"] = True
    session["game_state"] = "bidding"
    
    deck = create_deck()
    session["hand"] = sort_hand(deck[:13])
    session["bots"] = [
        {"name": random.choice(BOT_NAMES), "bid": random.randint(1, 5), "hand": deck[13:26]},
        {"name": random.choice(BOT_NAMES), "bid": random.randint(1, 5), "hand": deck[26:39]},
        {"name": random.choice(BOT_NAMES), "bid": random.randint(1, 5), "hand": deck[39:52]}
    ]
    return redirect('/')

@app.route('/bid/<int:b>')
def bid(b):
    session["my_bid"] = b
    session["game_state"] = "playing"
    return redirect('/')

@app.route('/play/<int:idx>')
def play(idx):
    # Basitçe kartı elden çıkarıyoruz (Gelişmiş yapay zeka bir sonraki adım)
    hand = session.get("hand", [])
    if not hand: return jsonify({"err": "Kart kalmadı!"})
    
    played = hand.pop(idx)
    session["hand"] = hand
    
    # Botlar da birer kart atar (Simülasyon)
    for b in session["bots"]:
        if b["hand"]: b["hand"].pop(0)
        
    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
