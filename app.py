import random, os
from flask import Flask, render_template_string, redirect, request, session

app = Flask(__name__)
app.secret_key = "batak_super_light_v1"

# --- VERİ TABANI ---
db = {"users": {"admin": {"ad": "Patron", "bakiye": 1000.0}}}
BOT_NAMES = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep"]

# --- KART KODLAMA SİSTEMİ (Hafifletilmiş) ---
# S: Spade, H: Heart, D: Diamond, C: Club
SUITS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

def create_hand():
    # Sadece 13 tane kısa kod üret (Örn: 'S12')
    hand = []
    for _ in range(13):
        s = random.choice(['S', 'H', 'D', 'C'])
        r = random.randint(0, 12)
        hand.append(f"{s}{r}")
    return hand

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; }
        .header { background:#111; padding:10px; display:flex; justify-content:space-between; border-bottom:2px solid #fcd535; }
        .table { position:relative; width:95vw; height:60vh; margin:15px auto; background:radial-gradient(#155d27, #0a3316); border:8px solid #5d3a1a; border-radius:150px; }
        .player { position:absolute; text-align:center; width:70px; }
        .p-top { top:10px; left:50%; transform:translateX(-50%); }
        .p-left { left:10px; top:50%; transform:translateY(-50%); }
        .p-right { right:10px; top:50%; transform:translateY(-50%); }
        .p-bottom { bottom:10px; left:50%; transform:translateX(-50%); }
        .avatar { background:#111; border:2px solid #fcd535; border-radius:50%; padding:10px; font-size:10px; }
        .hand { position:fixed; bottom:15px; width:100%; display:flex; justify-content:center; flex-wrap:wrap; gap:4px; }
        .card { width:40px; height:60px; background:white; color:black; border-radius:5px; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; cursor:pointer; font-size:12px; }
        .S, .C { color:black; } .H, .D { color:red; }
        .overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:100; }
        .btn { background:#fcd535; color:black; border:none; padding:15px 30px; border-radius:50px; font-weight:bold; cursor:pointer; text-decoration:none; }
    </style>
</head>
<body>
    {% if not session.user %}
        <div class="overlay">
            <h2 style="color:#fcd535">💎 VIP CASINO</h2>
            <form action="/login" method="post"><input type="text" name="u" placeholder="Adınız" required style="padding:10px;"><br><br><button class="btn">OTUR</button></form>
        </div>
    {% elif not session.in_game %}
        <div class="overlay">
            <h3 style="color:#fcd535">BAHİS: 20 €</h3>
            <a href="/start" class="btn">BAŞLA</a>
        </div>
    {% endif %}

    <div class="header">
        <span>👤 {{ session.user }}</span>
        <span style="color:#fcd535">💰 {{ bakiye }} €</span>
        <a href="/logout" style="color:red; text-decoration:none; font-size:12px;">KALK</a>
    </div>

    <div class="table">
        <div class="player p-top"><div class="avatar">{{ session.bots[0] }}</div></div>
        <div class="player p-left"><div class="avatar">{{ session.bots[1] }}</div></div>
        <div class="player p-right"><div class="avatar">{{ session.bots[2] }}</div></div>
        <div class="player p-bottom"><div class="avatar">SİZ</div></div>
        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); opacity:0.1; font-size:40px; font-weight:bold;">BATAK</div>
    </div>

    <div class="hand">
        {% for card_code in session.hand %}
            <div class="card {{ card_code[0] }}" onclick="location.href='/play/{{ loop.index0 }}'">
                <span>{{ ranks[card_code[1:]|int] }}</span>
                <span>{{ suits[card_code[0]] }}</span>
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
    return render_template_string(HTML, bakiye=b, suits=SUITS, ranks=RANKS)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]: db["users"][u] = {"bakiye": 1000.0}
    session["bots"] = random.sample(BOT_NAMES, 3)
    session["in_game"] = False
    return redirect('/')

@app.route('/start')
def start():
    u = session.get("user")
    if db["users"][u]["bakiye"] < 20: return "Bakiye Az!"
    db["users"][u]["bakiye"] -= 20
    session["in_game"] = True
    session["hand"] = create_hand()
    return redirect('/')

@app.route('/play/<int:idx>')
def play(idx):
    hand = session.get("hand", [])
    if hand:
        hand.pop(idx)
        session["hand"] = hand
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
