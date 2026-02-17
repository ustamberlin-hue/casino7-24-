import random, os
from flask import Flask, render_template_string, redirect, request, session

app = Flask(__name__)
app.secret_key = "batak_final_v5_fix"

# --- VERİ TABANI ---
db = {"users": {"admin": {"ad": "Patron", "bakiye": 1000.0}}}
BOTLAR = ["Mert", "Selin", "Caner"]

# --- OYUN MOTORU (HAFİFLETİLMİŞ) ---
def kartlari_hazirla():
    tipler = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    rakamlar = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    el = []
    for _ in range(13):
        t = random.choice(tipler)
        r = random.choice(rakamlar)
        el.append({'t': t[0], 's': t[1], 'v': r, 'p': rakamlar.index(r)})
    return sorted(el, key=lambda x: (x['t'], x['p']))

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; overflow:hidden; }
        .header { background:#111; padding:10px; display:flex; justify-content:space-between; border-bottom:2px solid #fcd535; }
        .table { position:relative; width:95vw; height:60vh; margin:15px auto; background:radial-gradient(#155d27, #0a3316); border:8px solid #5d3a1a; border-radius:150px; box-shadow: inset 0 0 50px #000; }
        .player { position:absolute; text-align:center; width:70px; font-size:10px; }
        .p-top { top:10px; left:50%; transform:translateX(-50%); }
        .p-left { left:10px; top:50%; transform:translateY(-50%); }
        .p-right { right:10px; top:50%; transform:translateY(-50%); }
        .p-bottom { bottom:10px; left:50%; transform:translateX(-50%); }
        .avatar { background:#111; border:2px solid #fcd535; border-radius:50%; padding:8px; font-weight:bold; }
        .arena { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:160px; height:120px; }
        .p-card { position:absolute; width:40px; height:60px; background:white; color:black; border-radius:5px; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; border:1px solid #000; }
        .pos-bottom { bottom:0; left:50%; transform:translateX(-50%); }
        .pos-top { top:0; left:50%; transform:translateX(-50%); }
        .pos-left { left:0; top:50%; transform:translateY(-50%); }
        .pos-right { right:0; top:50%; transform:translateY(-50%); }
        .hand { position:fixed; bottom:15px; width:100%; display:flex; justify-content:center; gap:3px; overflow-x:auto; padding:5px; }
        .card { width:40px; height:60px; background:white; color:black; border-radius:5px; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; cursor:pointer; font-size:11px; flex-shrink:0; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }
        .overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:100; }
        .btn { background:#fcd535; color:black; border:none; padding:15px 30px; border-radius:50px; font-weight:bold; cursor:pointer; text-decoration:none; }
    </style>
</head>
<body>
    {% if not session.user %}
        <div class="overlay">
            <h2 style="color:#fcd535">💎 VIP BATAK</h2>
            <form action="/login" method="post"><input type="text" name="u" placeholder="Adınız" required style="padding:10px; border-radius:5px;"><br><br><button class="btn">OTUR</button></form>
        </div>
    {% elif not session.in_game %}
        <div class="overlay">
            <h3 style="color:#fcd535">BAHİS: 20 €</h3>
            <a href="/start" class="btn">OYUNA BAŞLA</a>
        </div>
    {% endif %}

    <div class="header">
        <span>👤 {{ session.user }}</span>
        <span style="color:#fcd535">💰 {{ bakiye }} €</span>
        <a href="/logout" style="color:red; text-decoration:none;">ÇIK</a>
    </div>

    <div class="table">
        <div class="player p-top"><div class="avatar">{{ session.bots[0] }}</div></div>
        <div class="player p-left"><div class="avatar">{{ session.bots[1] }}</div></div>
        <div class="player p-right"><div class="avatar">{{ session.bots[2] }}</div></div>
        <div class="player p-bottom"><div class="avatar">SİZ</div></div>
        <div class="arena">
            {% for c in session.arena %}
                <div class="p-card pos-{{ c.p }} {{ c.t }}"><span>{{ c.v }}</span><span>{{ c.s }}</span></div>
            {% endfor %}
        </div>
    </div>

    <div class="hand">
        {% for c in session.hand %}
            <div class="card {{ c.t }}" onclick="location.href='/play/{{ loop.index0 }}'">
                <span>{{ c.v }}</span><span>{{ c.s }}</span>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    u = session.get("user")
    if not u: return render_template_string(HTML)
    b = db["users"].get(u, {"bakiye": 0})["bakiye"]
    return render_template_string(HTML, bakiye=b)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]: db["users"][u] = {"bakiye": 1000.0}
    session["bots"] = BOTLAR
    session["in_game"] = False
    session["arena"] = []
    return redirect('/')

@app.route('/start')
def start():
    u = session.get("user")
    if db["users"][u]["bakiye"] < 20: return "Yetersiz Bakiye"
    db["users"][u]["bakiye"] -= 20
    session["in_game"] = True
    session["hand"] = kartlari_hazirla()
    session["arena"] = []
    return redirect('/')

@app.route('/play/<int:idx>')
def play(idx):
    hand = session.get("hand", [])
    if hand and idx < len(hand):
        c = hand.pop(idx)
        session["hand"] = hand
        session["arena"] = [
            {'p': 'bottom', 't': c['t'], 's': c['s'], 'v': c['v']},
            {'p': 'top', 't': 'spade', 's': '♠', 'v': 'A'},
            {'p': 'left', 't': 'heart', 's': '♥', 'v': 'K'},
            {'p': 'right', 't': 'diamond', 's': '♦', 'v': 'Q'}
        ]
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # RENDER İÇİN KRİTİK AYAR
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
