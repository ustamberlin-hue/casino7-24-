import random, os
from flask import Flask, render_template_string, redirect, request, session, jsonify

app = Flask(__name__)
app.secret_key = "casino724_premium_key"

# --- VERİ TABANI ---
db = {
    "users": {
        "admin": {"pw": "1234", "role": "ADMIN", "ad": "Patron", "bakiye": 1000.0} # Bakiyeni 1000 yaptım Patron!
    },
    "basvurular": [],
    "bakiye_talepleri": []
}

def format_euro(v): return "{:,.2f} €".format(v).replace(",", "X").replace(".", ",").replace("X", ".")

# --- 20 POPÜLER OYUN LİSTESİ ---
OYUNLAR = [
    {"id": "s1", "ad": "Sweet Bonanza", "img": "https://img.freepik.com/premium-vector/casino-slot-machine-with-candy-icons_24908-62025.jpg"},
    {"id": "s2", "ad": "Gates of Olympus", "img": "https://img.freepik.com/premium-vector/olympus-god-zeus-concept_23-2148618451.jpg"},
    {"id": "s3", "ad": "Fruit Party", "img": "https://img.freepik.com/free-vector/set-fruit-icons-casino-slot-machine_24908-56540.jpg"},
    {"id": "s4", "ad": "The Dog House", "img": "https://img.freepik.com/free-vector/dog-house-concept-illustration_114360-1043.jpg"},
    {"id": "s5", "ad": "Sugar Rush", "img": "https://img.freepik.com/free-vector/candyland-concept-illustration_114360-1011.jpg"},
    {"id": "s6", "ad": "Big Bass Bonanza", "img": "https://img.freepik.com/free-vector/fishing-concept-illustration_114360-1205.jpg"},
    {"id": "s7", "ad": "Wild West Gold", "img": "https://img.freepik.com/free-vector/cowboy-concept-illustration_114360-1345.jpg"},
    {"id": "s8", "ad": "Starlight Princess", "img": "https://img.freepik.com/free-vector/anime-princess-concept-illustration_114360-1456.jpg"},
    {"id": "s9", "ad": "Wanted Dead or Wild", "img": "https://img.freepik.com/free-vector/wild-west-concept-illustration_114360-1567.jpg"},
    {"id": "s10", "ad": "Buffalo King", "img": "https://img.freepik.com/free-vector/buffalo-concept-illustration_114360-1678.jpg"},
    {"id": "s11", "ad": "Gems Bonanza", "img": "https://img.freepik.com/free-vector/gems-concept-illustration_114360-1789.jpg"},
    {"id": "s12", "ad": "Madame Destiny", "img": "https://img.freepik.com/free-vector/fortune-teller-concept-illustration_114360-1890.jpg"},
    {"id": "s13", "ad": "Joker Jewels", "img": "https://img.freepik.com/free-vector/joker-concept-illustration_114360-1901.jpg"},
    {"id": "s14", "ad": "Fire Strike", "img": "https://img.freepik.com/free-vector/fire-concept-illustration_114360-2012.jpg"},
    {"id": "s15", "ad": "Book of Dead", "img": "https://img.freepik.com/free-vector/egypt-concept-illustration_114360-2123.jpg"},
    {"id": "s16", "ad": "Legacy of Egypt", "img": "https://img.freepik.com/free-vector/pharaoh-concept-illustration_114360-2234.jpg"},
    {"id": "s17", "ad": "Wolf Gold", "img": "https://img.freepik.com/free-vector/wolf-concept-illustration_114360-2345.jpg"},
    {"id": "s18", "ad": "Great Rhino", "img": "https://img.freepik.com/free-vector/rhino-concept-illustration_114360-2456.jpg"},
    {"id": "s19", "ad": "Chilli Heat", "img": "https://img.freepik.com/free-vector/chilli-concept-illustration_114360-2567.jpg"},
    {"id": "s20", "ad": "Mustang Gold", "img": "https://img.freepik.com/free-vector/horse-concept-illustration_114360-2678.jpg"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
        .header { background:linear-gradient(90deg, #fcd535, #ffb800); color:black; text-align:center; padding:15px; font-weight:bold; }
        .card { background:#16181c; margin:10px; padding:15px; border-radius:12px; border:1px solid #333; }
        .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding:10px; }
        .game-card { background:#1c1f26; border-radius:12px; overflow:hidden; border:1px solid #444; text-align:center; cursor:pointer; }
        .game-card img { width:100%; height:110px; object-fit:cover; display:block; }
        .btn { background:#fcd535; color:black; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer; }
        .nav { display:flex; background:#16181c; border-top:1px solid #333; position:fixed; bottom:0; width:100%; z-index:99; }
        .nav-btn { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:12px; }
        #modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
        .slot-box { background:#1c1f26; padding:20px; border-radius:20px; border:2px solid #fcd535; width:85%; max-width:400px; text-align:center; }
        .reels { display:flex; justify-content:center; gap:10px; margin:20px 0; }
        .reel { background:black; border:2px solid #444; width:70px; height:80px; display:flex; align-items:center; justify-content:center; font-size:40px; border-radius:10px; }
    </style>
</head>
<body>
    <div class="header">🎰 CASINO7-24 OFFICIAL</div>

    {% if not session.user %}
        <div style="padding:30px;">
            <h3>Giriş Yap</h3>
            <form action="/login" method="post">
                <input type="text" name="u" placeholder="Kullanıcı Adı" style="width:100%; padding:12px; margin-bottom:10px; background:black; color:white; border:1px solid #333;">
                <input type="password" name="p" placeholder="Şifre" style="width:100%; padding:12px; margin-bottom:20px; background:black; color:white; border:1px solid #333;">
                <button class="btn">GİRİŞ</button>
            </form>
        </div>
    {% else %}
        <div class="card" style="text-align:center; border-bottom:3px solid #0ecb81;">
            BAKİYE: <b id="main-bal" style="color:#0ecb81; font-size:22px;">{{ fmt(bakiye) }}</b>
        </div>

        {% if p == 'ADMIN' %}
            <div style="padding:10px;">
                <h3>Panel</h3>
                {% if not db.basvurular %} <p>Bekleyen başvuru yok.</p> {% endif %}
                {% for b in db.basvurular %}
                <div class="card">{{ b.u }} <a href="/onay/{{loop.index0}}" style="color:lime;">[ONAYLA]</a></div>
                {% endfor %}
            </div>
        {% else %}
            <div class="grid">
                {% for g in oyunlar %}
                <div class="game-card" onclick="openSlot('{{ g.ad }}')">
                    <img src="{{ g.img }}" onerror="this.src='https://via.placeholder.com/150/1c1f26/fcd535?text=Casino+Game'">
                    <div style="padding:8px; font-size:12px; font-weight:bold;">{{ g.ad }}</div>
                </div>
                {% endfor %}
            </div>
        {% endif %}

        <div id="modal">
            <div class="slot-box">
                <h2 id="st" style="color:#fcd535; margin-top:0;">Oyun</h2>
                <div class="reels">
                    <div id="r1" class="reel">🍒</div><div id="r2" class="reel">🍋</div><div id="r3" class="reel">💎</div>
                </div>
                <select id="bet" style="width:100%; padding:10px; margin-bottom:10px; background:black; color:white; border:1px solid #444;">
                    <option value="1">1.00 €</option><option value="5" selected>5.00 €</option><option value="10">10.00 €</option>
                </select>
                <button id="sb" class="btn" onclick="spin()">SPIN ÇEVİR</button>
                <button onclick="document.getElementById('modal').style.display='none'" style="background:none; border:none; color:#777; margin-top:15px; cursor:pointer;">Kapat</button>
            </div>
        </div>

        <div class="nav">
            <a href="/" class="nav-btn">🎰 OYUNLAR</a>
            <a href="/?p=ADMIN" class="nav-btn">⚙️ PANEL</a>
            <a href="/logout" class="nav-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <script>
    function openSlot(n){ document.getElementById('st').innerText=n; document.getElementById('modal').style.display='flex'; }
    async function spin(){
        let b = document.getElementById('bet').value;
        let res = await fetch('/spin', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'bet='+b});
        let d = await res.json();
        if(d.error){ alert(d.error); return; }
        document.getElementById('sb').disabled = true;
        let syms = ["🍒","🍋","💎","7️⃣","🍉"];
        let count = 0;
        let iv = setInterval(()=>{
            document.getElementById('r1').innerText=syms[Math.floor(Math.random()*5)];
            document.getElementById('r2').innerText=syms[Math.floor(Math.random()*5)];
            document.getElementById('r3').innerText=syms[Math.floor(Math.random()*5)];
            if(count++ > 12){
                clearInterval(iv);
                document.getElementById('r1').innerText=d.r[0];
                document.getElementById('r2').innerText=d.r[1];
                document.getElementById('r3').innerText=d.r[2];
                document.getElementById('main-bal').innerText=d.nb;
                document.getElementById('sb').disabled = false;
                if(d.w > 0) alert("TEBRİKLER! "+d.w+" € KAZANDIN!");
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
    u_data = db["users"].get(u, {"bakiye":0})
    return render_template_string(HTML, p=request.args.get('p'), bakiye=u_data['bakiye'], oyunlar=OYUNLAR, db=db, fmt=format_euro)

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('u'), request.form.get('p')
    if u in db["users"] and db["users"][u]["pw"] == p: session["user"] = u
    return redirect('/')

@app.route('/spin', methods=['POST'])
def spin():
    u = session.get("user")
    if not u: return jsonify({"error": "Giriş yapmalısınız!"})
    bet = float(request.form.get('bet', 0))
    if db["users"][u]["bakiye"] < bet: return jsonify({"error": "Bakiye Yetersiz!"})
    
    db["users"][u]["bakiye"] -= bet
    is_win = random.random() < 0.25 # Kasa her zaman avantajlı
    win_amt = 0
    syms = ["🍒", "🍋", "💎", "7️⃣", "🍉"]
    
    if is_win:
        s = random.choice(syms)
        reels = [s, s, s]
        win_amt = bet * random.choice([2, 5, 10])
        db["users"][u]["bakiye"] += win_amt
    else:
        reels = random.sample(syms, 3)
        
    return jsonify({"r": reels, "w": win_amt, "nb": format_euro(db["users"][u]["bakiye"])})

@app.route('/onay/<int:id>')
def onay(id):
    if session.get("user") == "admin" and len(db["basvurular"]) > id:
        b = db["basvurular"].pop(id)
        db["users"][b['u']] = {"pw": b['p'], "ad": b['u'], "bakiye": 0}
    return redirect('/?p=ADMIN')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
