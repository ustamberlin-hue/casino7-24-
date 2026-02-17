import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "batak_stable_v1_2026"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "ad": "Patron", "bakiye": 5000.0}},
}

BOT_NAMES = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep", "Volkan", "Buse"]

# --- KART MOTORU ---
def get_clean_deck():
    suits = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    deck = []
    for sn, ss in suits:
        for r in ranks:
            deck.append({'suit': sn, 'sym': ss, 'rank': r, 'val': ranks.index(r)})
    random.shuffle(deck)
    return deck

def sort_my_hand(hand):
    # Batak sırası: Maça > Kupa > Karo > Sinek
    order = {'spade': 4, 'heart': 3, 'diamond': 2, 'club': 1}
    return sorted(hand, key=lambda x: (order[x['suit']], x['val']), reverse=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; }
        .header { background:rgba(0,0,0,0.8); padding:10px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fcd535; }
        .table { position:relative; width:95%; height:55vh; margin:20px auto; background:radial-gradient(#1a7a35, #083316); border:8px solid #3d2611; border-radius:100px; box-shadow: inset 0 0 50px #000; }
        .player { position:absolute; text-align:center; width:70px; }
        .p0 { bottom:-20px; left:50%; transform:translateX(-50%); } 
        .p1 { left:0px; top:50%; transform:translateY(-50%); }  
        .p2 { top:0px; left:50%; transform:translateX(-50%); }   
        .p3 { right:0px; top:50%; transform:translateY(-50%); } 
        .avatar { background:#111; border:2px solid #fcd535; border-radius:50%; padding:10px; font-size:10px; }
        .bid-tag { background:#fcd535; color:black; font-weight:bold; padding:2px; border-radius:5px; margin-top:3px; display:block; }
        .hand { position:fixed; bottom:10px; width:100%; display:flex; justify-content:center; }
        .card { width:45px; height:70px; background:white; color:black; border-radius:5px; margin-left:-15px; border:1px solid #000; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; cursor:pointer; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }
        .overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:99; }
        .btn { background:#fcd535; color:black; border:none; padding:12px 20px; border-radius:10px; font-weight:bold; cursor:pointer; margin:5px; }
    </style>
</head>
<body>
    {% if not session.user %}
    <div class="overlay">
        <h2>💎 VIP BATAK</h2>
        <form action="/login" method="post"><input type="text" name="u" placeholder="İsminiz" required style="padding:10px;"><br><br><button class="btn">GİRİŞ</button></form>
    </div>
    {% elif not session.game_active %}
    <div class="overlay">
        <h3>BAHİS YATIR</h3>
        <a href="/start/50"><button class="btn">50 €</button></a>
        <a href="/start/100"><button class="btn">100 €</button></a>
        <a href="/start/500"><button class="btn">500 €</button></a>
        <p>Bakiye: {{ bakiye }} €</p>
    </div>
    {% elif session.state == 'bid' %}
    <div class="overlay">
        <h3>İHALE SEÇ</h3>
        <div>{% for i in range(1, 11) %}<a href="/set_bid/{{i}}"><button class="btn" style="padding:10px;">{{i}}</button></a>{% endfor %}</div>
    </div>
    {% endif %}

    <div class="header">
        <span>💰 {{ bakiye }} €</span>
        <span style="color:#fcd535;">BAHİS: {{ session.bet }} €</span>
        <a href="/logout" style="color:red; text-decoration:none;">ÇIK</a>
    </div>

    <div class="table">
        <div class="player p1"><div class="avatar">{{ session.bot_names[0] }}<span class="bid-tag">İhale: {{ session.bot_bids[0] }}</span></div></div>
        <div class="player p2"><div class="avatar">{{ session.bot_names[1] }}<span class="bid-tag">İhale: {{ session.bot_bids[1] }}</span></div></div>
        <div class="player p3"><div class="avatar">{{ session.bot_names[2] }}<span class="bid-tag">İhale: {{ session.bot_bids[2] }}</span></div></div>
        <div class="player p0"><div class="avatar">SİZ<span class="bid-tag">İhale: {{ session.my_bid }}</span></div></div>
    </div>

    <div class="hand">
        {% for c in session.my_hand %}
        <div class="card {{ c.suit }}" onclick="location.href='/play/{{loop.index0}}'">
            <span>{{ c.rank }}</span><span>{{ c.sym }}</span>
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
    deck = get_clean_deck()
    session["my_hand"] = sort_my_hand(deck[:13])
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
    if hand:
        hand.pop(idx)
        session["my_hand"] = hand
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
