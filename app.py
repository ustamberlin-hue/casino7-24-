import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "batak_vip_stable_2026"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "bakiye": 5000.0}},
}

BOT_NAMES = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep", "Volkan", "Buse"]

# --- KART VE OYUN MANTIĞI ---
def get_sorted_hand():
    suits = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    # Sadece 13 kartlık el üretelim (Sunucuyu yormamak için)
    hand = []
    for _ in range(13):
        s = random.choice(suits)
        r = random.choice(ranks)
        hand.append({'suit': s[0], 'sym': s[1], 'rank': r, 'val': ranks.index(r)})
    # Batak Sıralaması: Maça > Kupa > Karo > Sinek
    order = {'spade': 4, 'heart': 3, 'diamond': 2, 'club': 1}
    return sorted(hand, key=lambda x: (order[x['suit']], x['val']), reverse=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#0a3316; color:white; font-family:sans-serif; margin:0; overflow-x:hidden; }
        .header { background:rgba(0,0,0,0.9); padding:12px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fcd535; }
        
        .table { 
            position:relative; width:92vw; height:50vh; margin:30px auto; 
            background:radial-gradient(#1a7a35, #083316); border:10px solid #3d2611; border-radius:150px; 
            box-shadow: inset 0 0 80px #000;
        }
        
        .player { position:absolute; text-align:center; min-width:80px; }
        .p0 { bottom:-35px; left:50%; transform:translateX(-50%); } 
        .p1 { left:-10px; top:50%; transform:translateY(-50%); }  
        .p2 { top:-35px; left:50%; transform:translateX(-50%); }   
        .p3 { right:-10px; top:50%; transform:translateY(-50%); } 
        
        .avatar { background:#111; border:2px solid #fcd535; border-radius:15px; padding:8px; font-size:11px; }
        .bid-tag { background:#fcd535; color:black; font-weight:bold; padding:2px 6px; border-radius:5px; margin-top:5px; display:inline-block; }

        .hand-container { position:fixed; bottom:15px; width:100%; display:flex; justify-content:center; }
        .card { 
            width:48px; height:75px; background:white; color:black; border-radius:6px; margin-left:-18px;
            border:1px solid #000; display:flex; flex-direction:column; align-items:center; justify-content:center;
            font-weight:bold; cursor:pointer; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); transition: 0.2s;
        }
        .card:hover { transform:translateY(-20px); z-index:100; border-color:#fcd535; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }

        .overlay { 
            position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); 
            display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:999;
        }
        .btn { background:#fcd535; color:black; border:none; padding:15px 30px; border-radius:50px; font-weight:bold; cursor:pointer; font-size:1rem; margin:10px; }
        .bid-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap:10px; }
        .bid-btn { background:none; border:2px solid #fcd535; color:white; width:45px; height:45px; border-radius:50%; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>

    {% if not session.user %}
        <div class="overlay">
            <h2 style="color:#fcd535;">💎 CASINO VIP BATAK</h2>
            <form action="/login" method="post" style="text-align:center;">
                <input type="text" name="u" placeholder="Takma Adınız" required style="padding:15px; border-radius:10px; border:none; width:220px;"><br>
                <button class="btn">MASAYA OTUR</button>
            </form>
        </div>
    {% elif not session.game_active %}
        <div class="overlay">
            <h3 style="color:#fcd535;">BAHİS TUTARINI SEÇİN</h3>
            <div style="display:flex; flex-wrap:wrap; justify-content:center;">
                <button class="btn" onclick="location.href='/start/50'">50 €</button>
                <button class="btn" onclick="location.href='/start/100'">100 €</button>
                <button class="btn" onclick="location.href='/start/500'">500 €</button>
            </div>
            <p>Bakiye: {{ bakiye }} €</p>
        </div>
    {% elif session.state == 'bid' %}
        <div class="overlay">
            <h3 style="color:#fcd535;">İHALE: KAÇ ALIRSIN?</h3>
            <div class="bid-grid">
                {% for i in range(1, 11) %}
                <button class="bid-btn" onclick="location.href='/set_bid/{{i}}'">{{i}}</button>
                {% endfor %}
            </div>
            <p style="font-size:12px; margin-top:20px;">Elinizdeki kartlara göre seçim yapın.</p>
        </div>
    {% endif %}

    <div class="header">
        <span style="color:#0ecb81; font-weight:bold;">💰 {{ bakiye }} €</span>
        <span style="color:#fcd535; font-weight:bold;">📍 BAHİS: {{ session.bet }} €</span>
        <a href="/logout" style="color:#ff4c4c; text-decoration:none; font-size:13px; font-weight:bold;">MASADAN KALK</a>
    </div>

    <div class="table">
        <div class="player p1"><div class="avatar">👤 {{ session.bot_names[0] }}<br><span class="bid-tag">İhale: {{ session.bot_bids[0] }}</span></div></div>
        <div class="player p2"><div class="avatar">👤 {{ session.bot_names[1] }}<br><span class="bid-tag">İhale: {{ session.bot_bids[1] }}</span></div></div>
        <div class="player p3"><div class="avatar">👤 {{ session.bot_names[2] }}<br><span class="bid-tag">İhale: {{ session.bot_bids[2] }}</span></div></div>
        <div class="player p0"><div class="avatar">⭐ SİZ<br><span class="bid-tag">İhale: {{ session.my_bid if session.my_bid else '?' }}</span></div></div>
        
        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); opacity:0.2;">
            <h2 style="margin:0; font-size:40px; color:white; border:2px solid white; padding:10px;">BATAK VIP</h2>
        </div>
    </div>

    <div class="hand-container">
        {% for c in session.my_hand %}
        <div class="card {{ c.suit }}" onclick="location.href='/play/{{loop.index0}}'">
            <div style="font-size:18px;">{{ c.rank }}</div>
            <div style="font-size:28px; margin-top:-5px;">{{ c.sym }}</div>
        </div>
        {% endfor %}
    </div>

</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    b = db["users"][u]["bakiye"] if u in db["users"] else 0
    return render_template_string(HTML, bakiye=b)

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
    session["bet"] = bet
    session["game_active"] = True
    session["state"] = "bid"
    session["my_hand"] = get_sorted_hand()
    session["bot_names"] = random.sample(BOT_NAMES, 3)
    session["bot_bids"] = [random.randint(1,4), random.randint(1,4), random.randint(1,4)]
    session["my_bid"] = 0
    return redirect('/')

@app.route('/set_bid/<int:b>')
def set_bid(b):
    session["my_bid"] = b
    session["state"] = "play"
    return redirect('/')

@app.route('/play/<int:idx>')
def play(idx):
    hand = session.get("my_hand", [])
    if hand and len(hand) > idx:
        hand.pop(idx)
        session["my_hand"] = hand
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # Render için Port ayarı
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
