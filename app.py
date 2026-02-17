import random, os
from flask import Flask, render_template_string, redirect, request, session

app = Flask(__name__)
app.secret_key = "batak_vip_real_logic_2026"

# --- VERİ TABANI ---
db = {"users": {"admin": {"ad": "Patron", "bakiye": 1000.0}}}
BOT_ISIMLERI = ["Mert", "Selin", "Caner", "Ece", "Hakan", "Zeynep", "Emre", "Derya"]

# --- KART VE OYUN MOTORU ---
def yeni_deste_ve_dagit():
    suits = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    deste = [{'type': s[0], 'sym': s[1], 'val': r, 'power': i} for s in suits for i, r in enumerate(ranks)]
    random.shuffle(deste)
    # Sadece oyuncunun elini ve bot isimlerini döndür (Hafıza dostu)
    return sorted(deste[:13], key=lambda x: (x['type'], x['power']))

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#073d1a; color:white; font-family:sans-serif; margin:0; overflow:hidden; }
        .header { background:#111; padding:10px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fcd535; }
        .table { 
            position:relative; width:95vw; height:60vh; margin:20px auto; 
            background:radial-gradient(#155d27, #0a3316); border:8px solid #5d3a1a; border-radius:150px; 
            box-shadow: inset 0 0 50px #000;
        }
        .player { position:absolute; text-align:center; width:80px; z-index:5; }
        .p-top { top:15px; left:50%; transform:translateX(-50%); }
        .p-left { left:15px; top:50%; transform:translateY(-50%); }
        .p-right { right:15px; top:50%; transform:translateY(-50%); }
        .p-bottom { bottom:15px; left:50%; transform:translateX(-50%); }
        .avatar { background:#111; border:2px solid #fcd535; border-radius:50%; padding:8px; font-size:11px; font-weight:bold; }
        
        .arena { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:200px; height:150px; }
        .played-card { position:absolute; width:45px; height:70px; background:white; color:black; border-radius:5px; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; border:1px solid #000; }
        /* Kartların Masadaki Pozisyonları */
        .pos-bottom { bottom:0; left:50%; transform:translateX(-50%); }
        .pos-top { top:0; left:50%; transform:translateX(-50%); }
        .pos-left { left:0; top:50%; transform:translateY(-50%); }
        .pos-right { right:0; top:50%; transform:translateY(-50%); }

        .hand { position:fixed; bottom:15px; width:100%; display:flex; justify-content:center; gap:4px; padding:0 10px; box-sizing:border-box; }
        .card { 
            width:42px; height:65px; background:white; color:black; border-radius:5px; border:1px solid #999; 
            display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:bold; cursor:pointer; font-size:12px;
        }
        .card:hover { transform:translateY(-15px); border:2px solid #fcd535; }
        .spade, .club { color:black; } .heart, .diamond { color:red; }
        
        .overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:100; }
        .btn-gold { background:#fcd535; color:black; border:none; padding:15px 30px; border-radius:50px; font-weight:bold; cursor:pointer; text-decoration:none; }
    </style>
</head>
<body>
    {% if not session.user %}
        <div class="overlay">
            <h2 style="color:#fcd535">💎 CASINO VIP BATAK</h2>
            <form action="/login" method="post"><input type="text" name="u" placeholder="Kullanıcı Adı" required style="padding:15px; border-radius:10px;"><br><br><button class="btn-gold">GİRİŞ</button></form>
        </div>
    {% elif not session.in_game %}
        <div class="overlay">
            <h3 style="color:#fcd535">MASA BAHİSİ: 20 €</h3>
            <p>Rakipler: {{ session.bots|join(', ') }}</p>
            <a href="/start" class="btn-gold">BAHİSİ YATIR VE BAŞLA</a>
        </div>
    {% endif %}

    <div class="header">
        <span>👤 {{ session.user }}</span>
        <span style="color:#fcd535; font-weight:bold;">💰 {{ bakiye }} €</span>
        <a href="/logout" style="color:red; text-decoration:none; font-size:12px;">MASADAN KALK</a>
    </div>

    <div class="table">
        <div class="player p-top"><div class="avatar">{{ session.bots[0] }}</div></div>
        <div class="player p-left"><div class="avatar">{{ session.bots[1] }}</div></div>
        <div class="player p-right"><div class="avatar">{{ session.bots[2] }}</div></div>
        <div class="player p-bottom"><div class="avatar">SİZ</div></div>
        
        <div class="arena">
            {% for p in session.arena %}
                <div class="played-card pos-{{ p.pos }} {{ p.card.type }}">
                    <span>{{ p.card.val }}</span><span>{{ p.card.sym }}</span>
                </div>
            {% endfor %}
        </div>
    </div>

    <div class="hand">
        {% for c in session.get('hand', []) %}
            <div class="card {{ c.type }}" onclick="location.href='/play/{{ loop.index0 }}'">
                <span>{{ c.val }}</span><span>{{ c.sym }}</span>
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
    b = db["users"][u]["bakiye"]
    return render_template_string(HTML, bakiye=b)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    session["user"] = u
    if u not in db["users"]: db["users"][u] = {"bakiye": 1000.0}
    session["bots"] = random.sample(BOT_ISIMLERI, 3)
    session["in_game"] = False
    return redirect('/')

@app.route('/start')
def start():
    u = session.get("user")
    if db["users"][u]["bakiye"] < 20: return "Yetersiz Bakiye"
    db["users"][u]["bakiye"] -= 20
    session["in_game"] = True
    session["hand"] = yeni_deste_ve_dagit()
    session["arena"] = []
    return redirect('/')

@app.route('/play/<int:idx>')
def play(idx):
    hand = session.get("hand", [])
    if not hand or idx >= len(hand): return redirect('/')
    
    # 1. Oyuncunun (SİZ) kartı
    player_card = hand.pop(idx)
    session["hand"] = hand
    
    # 2. Botlar sırayla kart atar (Gerçek Batak Mantığı: Aynı türden veya rastgele)
    suits = [('spade','♠'), ('heart','♥'), ('diamond','♦'), ('club','♣')]
    ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    
    def random_card():
        s = random.choice(suits)
        r = random.choice(ranks)
        return {'type': s[0], 'sym': s[1], 'val': r, 'power': ranks.index(r)}

    # Masayı kur
    arena = [
        {'pos': 'bottom', 'card': player_card},
        {'pos': 'top', 'card': random_card()},
        {'pos': 'left', 'card': random_card()},
        {'pos': 'right', 'card': random_card()}
    ]
    
    session["arena"] = arena
    # Not: Gerçek batakta burada "eli kim kazandı" hesabı yapılır, bir sonraki adımda ekleyebiliriz.
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
