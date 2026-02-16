import random
import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, redirect, request, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = "gokay_holding_v24_precision"

# --- VERİ TABANI ---
db = {
    "users": {"admin": {"pw": "1234", "role": "ADMIN", "ad": "Patron", "bakiye": 1250000}},
    "basvurular": [],
    "bakiye_talepleri": [],
    "kuponlar": []
}

def format_euro(value):
    return "{:,.0f}".format(value).replace(",", ".")

TAKIMLAR = ["GS", "FB", "BJK", "TS", "Real Madrid", "Barca", "Man City", "Arsenal", "Bayern", "Milan", "Inter", "Liverpool", "Napoli", "Dortmund", "PSG", "Ajax", "Chelsea", "Atletico", "Roma", "Lyon", "Porto", "Benfica"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
LIGLER = ["Süper Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League"]

def bulten_olustur():
    bulten = []
    simdi = datetime.now()
    for i in range(7):
        gun_tarih = simdi + timedelta(days=i)
        gun_adi = GUNLER[gun_tarih.weekday()]
        tarih_str = gun_tarih.strftime("%d.%m")
        mac_sayisi = random.randint(20, 30)
        for _ in range(mac_sayisi):
            t1, t2 = random.sample(TAKIMLAR, 2)
            saat_obj = gun_tarih.replace(hour=random.randint(0, 23), minute=random.choice([0, 15, 30, 45]), second=0)
            bulten.append({
                "id": str(random.randint(10000, 99999)),
                "gun": gun_adi, "tarih": tarih_str, "saat": saat_obj.strftime("%H:%M"),
                "tam_zaman": saat_obj, "lig": random.choice(LIGLER),
                "t1": t1, "t2": t2,
                "oranlar": {"MS 1": round(random.uniform(1.3, 3.8), 2), "MS X": round(random.uniform(3.1, 4.0), 2), "MS 2": round(random.uniform(2.1, 5.0), 2)}
            })
    return sorted(bulten, key=lambda x: x['tam_zaman'])

TUM_BULTEN_HAVUZU = bulten_olustur()

def aktif_bulten_getir():
    simdi = datetime.now()
    return [m for m in TUM_BULTEN_HAVUZU if m['tam_zaman'] > simdi]

def kuponlari_guncelle():
    simdi = datetime.now()
    for k in db["kuponlar"]:
        if k["durum"] in ["WINNER ✅", "LOST ❌", "İPTAL EDİLDİ ↩️"]:
            continue
        bitis_vakti = k["bitis_zamani"] + timedelta(minutes=95)
        if simdi < k["baslangic_zamani"]:
            k["durum"] = "Bekliyor... ⏱️"
        elif k["baslangic_zamani"] <= simdi <= bitis_vakti:
            k["durum"] = "Canlıda... ⚽"
        elif simdi > bitis_vakti:
            kazandi = random.random() < 0.3
            if kazandi:
                k["durum"] = "WINNER ✅"
                k["kazanc"] = int(k["misli"] * k["oran"])
                if k["u"] in db["users"]: 
                    db["users"][k["u"]]["bakiye"] += k["kazanc"]
            else:
                k["durum"] = "LOST ❌"
                k["kazanc"] = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background:#0a0b0d; color:white; font-family:sans-serif; margin:0; padding-bottom:120px; }
        .header { background:#fcd535; color:black; text-align:center; padding:15px; font-weight:bold; position:sticky; top:0; z-index:100; }
        .card { background:#16181c; margin:10px; padding:12px; border-radius:12px; border:1px solid #333; position:relative; }
        .input { width:100%; padding:14px; margin-bottom:15px; background:black; color:white; border:1px solid #444; border-radius:10px; box-sizing:border-box; }
        .btn { background:#fcd535; color:black; border:none; padding:14px; border-radius:10px; font-weight:bold; width:100%; cursor:pointer; text-decoration:none; display:block; text-align:center; }
        .btn-red { background:#ff4444; color:white; }
        .btn-green { background:#0ecb81; color:white; }
        .odds-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:5px; margin-top:10px; }
        .odd-btn { background:#262a33; border:1px solid #333; color:#fcd535; padding:8px 2px; border-radius:6px; text-align:center; font-size:11px; cursor:pointer; }
        .odd-btn.selected { background:#fcd535; color:black; font-weight:bold; }
        .footer { position:fixed; bottom:0; width:100%; background:#16181c; display:flex; border-top:1px solid #333; z-index:100; }
        .f-btn { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:11px; }
        .bet-slip { position:fixed; bottom:55px; width:100%; background:#fcd535; color:black; padding:12px; display:none; z-index:99; box-sizing:border-box; border-radius:15px 15px 0 0; }
        .error-msg { background:#ff4444; color:white; padding:10px; border-radius:8px; margin-bottom:15px; text-align:center; font-size:13px; }
        
        .horizontal-menu { display:flex; overflow-x:auto; padding:10px; gap:10px; white-space:nowrap; scrollbar-width: none; }
        .horizontal-menu::-webkit-scrollbar { display:none; }
        .menu-item { background:#262a33; padding:8px 18px; border-radius:20px; font-size:12px; color:#fcd535; border:1px solid #333; cursor:pointer; min-width: fit-content; }
        .menu-item.active { background:#fcd535; color:black; font-weight:bold; }

        /* --- CASINO ÖZEL --- */
        .game-tabs { display:flex; gap:5px; padding:10px; overflow-x:auto; }
        .tab-btn { flex:1; padding:10px; background:#262a33; color:#fcd535; border:1px solid #444; border-radius:8px; font-size:11px; white-space:nowrap; }
        .tab-btn.active { background:#fcd535; color:black; font-weight:bold; }
        .reels { display:flex; justify-content:center; gap:8px; margin:20px 0; }
        .slot-reel { background:linear-gradient(180deg, #000, #222); border:2px solid #fcd535; height:80px; width:65px; display:flex; align-items:center; justify-content:center; font-size:35px; border-radius:12px; box-shadow: 0 0 15px rgba(252,213,53,0.2); }
        .winning { animation: blink 0.3s infinite; border-color: #0ecb81; box-shadow: 0 0 20px #0ecb81; }
        @keyframes blink { 0% { opacity:1; } 50% { opacity:0.6; } 100% { opacity:1; } }
    </style>
</head>
<body>
    <div class="header">🏢 GOKAYBETT HOLDİNG (EU)</div>

    {% if not session.user %}
        <div style="padding:30px;">
            {% if request.args.get('mod') == 'kayit' %}
                <h3 style="text-align:center;">Branch Application</h3>
                {% if request.args.get('hata') == 'isim' %}<div class="error-msg">Username taken!</div>{% endif %}
                <form action="/islem/kayit" method="post">
                    <input type="text" name="ad" placeholder="Full Name" class="input" required>
                    <input type="text" name="u" placeholder="Username" class="input" required>
                    <input type="password" name="p" placeholder="Password" class="input" required>
                    <button class="btn">SEND APPLICATION</button>
                    <a href="/" style="color:#fcd535; display:block; text-align:center; margin-top:15px; text-decoration:none;">Back to Login</a>
                </form>
            {% else %}
                <h3 style="text-align:center;">Terminal Login</h3>
                {% if request.args.get('hata') == 'login' %}<div class="error-msg">Invalid Username or Password!</div>{% endif %}
                {% if request.args.get('msg') == 'ok' %}<div class="error-msg" style="background:#0ecb81;">Application Sent! Wait for Approval.</div>{% endif %}
                <form action="/islem/giris" method="post">
                    <input type="text" name="u" placeholder="Username" class="input" required>
                    <input type="password" name="p" placeholder="Password" class="input" required>
                    <button class="btn">LOG IN</button>
                    <a href="/?mod=kayit" style="color:#fcd535; display:block; text-align:center; margin-top:15px; text-decoration:none;">Apply for Branch</a>
                </form>
            {% endif %}
        </div>
    {% else %}
        {% if page == 'BULTEN' %}
            <div class="horizontal-menu">
                <div class="menu-item active" onclick="filterBy('lig', 'all', this)">Tüm Ligler</div>
                {% for lig in ligler %}<div class="menu-item" onclick="filterBy('lig', '{{lig}}', this)">{{ lig }}</div>{% endfor %}
            </div>
            <div class="card" style="border-left:4px solid #0ecb81; display:flex; justify-content:space-between; align-items:center;">
                <b>BALANCE: <span id="top-balance" style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b>
                <button onclick="document.getElementById('bakiyeBox').style.display='block'" class="odd-btn">REQUEST €</button>
            </div>
            <div id="bakiyeBox" class="card" style="display:none; border:1px dashed #fcd535;">
                <form action="/islem/bakiye_iste" method="post">
                    <input type="number" name="m" placeholder="Amount (€)" class="input" required>
                    <button class="btn btn-green">SEND REQUEST</button>
                    <button type="button" onclick="this.parentElement.parentElement.style.display='none'" class="btn btn-red" style="margin-top:5px; padding:5px;">Cancel</button>
                </form>
            </div>
            <div id="mac-listesi">
                {% for m in bulten %}
                    <div class="card match-card" data-lig="{{m.lig}}" data-gun="{{m.gun}}">
                        <div style="font-size:10px; color:#fcd535; font-weight:bold;">{{ m.lig }} | {{ m.tarih }} | {{ m.saat }}</div>
                        <div style="text-align:center; font-weight:bold;">{{ m.t1 }} vs {{ m.t2 }}</div>
                        <div class="odds-grid">
                            {% for k, v in m.oranlar.items() %}
                            <div class="odd-btn" onclick="sel(this, '{{m.id}}', '{{m.t1}} vs {{m.t2}}', '{{k}}', {{v}})">
                                <small style="display:block; color:#888;">{{k}}</small>{{v}}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
            </div>
            <div id="slip" class="bet-slip">
                <form action="/islem/kupon_yap" method="post">
                    <input type="hidden" name="toplam_oran" id="totalO_input" value="1.00">
                    <input type="hidden" name="match_data" id="match_data_input">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <input type="number" name="misli" id="misli" value="100" min="1" style="width:70px; padding:5px;" oninput="calc()">
                        <b>WIN: <span id="win">0</span> €</b>
                        <button type="submit" class="btn" style="width:auto; padding:8px 15px;">BET</button>
                    </div>
                </form>
            </div>

        {% elif page == 'CASINO' %}
            <div class="game-tabs">
                <button class="tab-btn active" onclick="switchGame('classic', this)">GOKAY CLASSIC</button>
                <button class="tab-btn" onclick="switchGame('wild', this)">WILD FIRE 🔥</button>
                <button class="tab-btn" onclick="switchGame('deluxe', this)">FRUIT DELUXE 💎</button>
            </div>

            <div class="card" style="text-align:center; border-top: 3px solid #fcd535;">
                <h3 id="game-title" style="color:#fcd535; margin-bottom:5px;">🎰 GOKAY CLASSIC</h3>
                <div class="reels">
                    <div id="reel1" class="slot-reel">🍒</div>
                    <div id="reel2" class="slot-reel">🍋</div>
                    <div id="reel3" class="slot-reel">7️⃣</div>
                </div>
                
                <div style="margin-bottom:15px;">
                    <b>Bakiye: <span id="slot-balance" style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b><br><br>
                    <b>BAHİS: </b>
                    <select id="slot-bet" class="input" style="width:120px; display:inline-block; padding:8px; margin:0;">
                        <option value="0.5">0.50 €</option>
                        <option value="1">1.00 €</option>
                        <option value="2">2.00 €</option>
                        <option value="3">3.00 €</option>
                        <option value="5">5.00 €</option>
                        <option value="7">7.00 €</option>
                        <option value="10">10.00 €</option>
                    </select>
                </div>
                
                <button onclick="spin()" id="spin-btn" class="btn" style="font-size:18px; letter-spacing:1px;">SPIN (ÇEVİR)</button>
                <p id="slot-res" style="margin-top:15px; font-weight:bold; min-height:22px;"></p>
                <p style="font-size:10px; color:#888; border-top:1px solid #333; padding-top:10px;">Gokaybett Gaming System (RTP %30)</p>
            </div>

        {% elif page == 'SETTINGS' %}
            <div class="card">
                <h3>Account Settings</h3>
                <form action="/islem/sifre_degistir" method="post">
                    <input type="password" name="p" placeholder="New Password" class="input" required>
                    <button class="btn">UPDATE PASSWORD</button>
                </form>
            </div>

        {% elif page == 'ADMIN' and session.user == 'admin' %}
            <div style="padding:10px;">
                <h3 style="color:#fcd535;">Admin Panel</h3>
                <h4>Applications</h4>
                {% for b in db.basvurular %}
                    <div class="card">
                        <b>{{ b.ad }}</b> (@{{ b.u }})
                        <div style="display:flex; gap:5px; margin-top:10px;">
                            <a href="/islem/onay/{{ loop.index0 }}" class="btn btn-green" style="flex:1; padding:8px;">APPROVE</a>
                            <a href="/islem/red/{{ loop.index0 }}" class="btn btn-red" style="flex:1; padding:8px;">REJECT</a>
                        </div>
                    </div>
                {% endfor %}
                <h4>Balance Requests</h4>
                {% for t in db.bakiye_talepleri %}
                    <div class="card">
                        {{ t.u }}: {{ fmt(t.m) }} €
                        <div style="display:flex; gap:5px; margin-top:5px;">
                            <a href="/islem/bakiye_onay/{{ loop.index0 }}" class="btn btn-green" style="flex:1; padding:5px;">CONFIRM</a>
                            <a href="/islem/bakiye_iptal/{{ loop.index0 }}" class="btn btn-red" style="flex:1; padding:5px;">CANCEL</a>
                        </div>
                    </div>
                {% endfor %}
            </div>

        {% elif page == 'KUPONLAR' %}
            <div style="padding:10px;">
                <h3 style="color:#fcd535;">My Coupons</h3>
                {% for k in db.kuponlar if k.u == session.user %}
                <div class="card">
                    <div style="font-size:11px; color:#888;">{{ k.tarih }}</div>
                    <div style="margin:5px 0;"><b>Matches:</b> {{ k.detay }}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span>{{ k.misli }}€ @ {{ k.oran }}</span>
                        <span style="font-weight:bold; color:{% if 'WINNER' in k.durum %}#0ecb81{% elif 'LOST' in k.durum %}#ff4444{% else %}#fcd535{% endif %};">{{ k.durum }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% endif %}

        <div class="footer">
            <a href="/p/BULTEN" class="f-btn">BÜLTEN</a>
            <a href="/p/CASINO" class="f-btn" style="color:#fcd535; font-weight:bold;">CASINO</a>
            <a href="/p/KUPONLAR" class="f-btn">KUPONLAR</a>
            <a href="/p/SETTINGS" class="f-btn">AYARLAR</a>
            {% if session.user == 'admin' %}<a href="/p/ADMIN" class="f-btn" style="color:#fcd535;">YÖNETİM</a>{% endif %}
            <a href="/logout" class="f-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <script>
        let selectedGame = 'classic';
        function switchGame(game, btn) {
            selectedGame = game;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const titles = {'classic':'🎰 GOKAY CLASSIC', 'wild':'🔥 WILD FIRE', 'deluxe':'💎 FRUIT DELUXE'};
            document.getElementById('game-title').innerText = titles[game];
        }

        function filterBy(type, value, el) {
            el.parentElement.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.match-card').forEach(card => {
                card.style.display = (value === 'all' || card.getAttribute('data-lig') === value) ? 'block' : 'none';
            });
        }
        let picks = [];
        function sel(el, id, teams, pick, odd) {
            el.classList.toggle('selected');
            picks.push({id, odd});
            document.getElementById('slip').style.display = 'block';
            document.getElementById('match_data_input').value = JSON.stringify(picks);
            calc();
        }
        function calc() {
            let o = picks.reduce((acc, c) => acc * c.odd, 1);
            let m = document.getElementById('misli').value || 0;
            document.getElementById('win').innerText = Math.floor(o * m).toLocaleString('de-DE');
        }

        async function spin() {
            const btn = document.getElementById('spin-btn');
            const bet = document.getElementById('slot-bet').value;
            const resText = document.getElementById('slot-res');
            btn.disabled = true;
            resText.innerText = "🌀 ÇEVRİLİYOR...";
            resText.style.color = "white";
            
            const response = await fetch('/islem/slot_spin', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `bet=${bet}&game=${selectedGame}`
            });
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                btn.disabled = false;
                resText.innerText = "";
                return;
            }

            let counter = 0;
            const symbols = ["🍒", "🍋", "🔔", "🍉", "🍇", "💎", "7️⃣"];
            const interval = setInterval(() => {
                document.getElementById('reel1').innerText = symbols[Math.floor(Math.random()*symbols.length)];
                document.getElementById('reel2').innerText = symbols[Math.floor(Math.random()*symbols.length)];
                document.getElementById('reel3').innerText = symbols[Math.floor(Math.random()*symbols.length)];
                counter++;
                if(counter > 15) {
                    clearInterval(interval);
                    document.getElementById('reel1').innerText = data.reels[0];
                    document.getElementById('reel2').innerText = data.reels[1];
                    document.getElementById('reel3').innerText = data.reels[2];
                    
                    if(data.win > 0) {
                        resText.innerText = "💰 TEBRİKLER! +" + data.win + " €";
                        resText.style.color = "#0ecb81";
                        document.querySelectorAll('.slot-reel').forEach(r => r.classList.add('winning'));
                    } else {
                        resText.innerText = "❌ TEKRAR DENE!";
                        resText.style.color = "#ff4444";
                        document.querySelectorAll('.slot-reel').forEach(r => r.classList.remove('winning'));
                    }
                    document.getElementById('slot-balance').innerText = data.new_balance + " €";
                    document.getElementById('top-balance').innerText = data.new_balance + " €";
                    btn.disabled = false;
                }
            }, 80);
        }
    </script>
</body>
</html>
"""

@app.route('/')
@app.route('/p/<page>')
def index(page='BULTEN'):
    u = session.get("user")
    u_data = db["users"].get(u, {"bakiye":0})
    kuponlari_guncelle()
    return render_template_string(HTML, bakiye=u_data['bakiye'], bulten=aktif_bulten_getir(), session=session, page=page, fmt=format_euro, db=db, ligler=LIGLER, gunler_liste=GUNLER)

@app.route('/islem/<aksiyon>', methods=['POST', 'GET'])
@app.route('/islem/<aksiyon>/<id>', methods=['POST', 'GET'])
def islem(aksiyon, id=None):
    if aksiyon == "giris":
        u, p = request.form.get('u', '').strip().lower(), request.form.get('p', '')
        if u in db["users"] and db["users"][u]["pw"] == p: 
            session["user"] = u
            return redirect('/')
        return redirect('/?hata=login')

    elif aksiyon == "slot_spin" and session.get("user"):
        u = session["user"]
        try:
            bet = float(request.form.get('bet', 0))
        except:
            return jsonify({"error": "Hatalı bahis!"})
            
        if db["users"][u]["bakiye"] < bet:
            return jsonify({"error": "Bakiye yetersiz!"})
        
        db["users"][u]["bakiye"] -= bet
        win = 0
        
        # --- PATRON AYARI: %70 KASA / %30 OYUNCU ---
        is_winner = random.random() < 0.30
        
        symbols = ["🍒", "🍋", "🔔", "🍉", "🍇", "💎", "7️⃣"]
        
        if is_winner:
            s = random.choice(symbols)
            reels = [s, s, s]
            # Çarpan: x2 ile x10 arası rastgele
            multiplier = random.choice([2, 3, 5, 10])
            win = int(bet * multiplier)
            db["users"][u]["bakiye"] += win
        else:
            reels = random.sample(symbols, 3)
            # Kaybetme durumunda aynı gelme ihtimalini sıfırla
            if reels[0] == reels[1] == reels[2]:
                reels[2] = symbols[(symbols.index(reels[2])+1) % len(symbols)]

        return jsonify({"reels": reels, "win": win, "new_balance": format_euro(db["users"][u]["bakiye"])})

    elif aksiyon == "kayit":
        u = request.form.get('u', '').strip().lower()
        db["basvurular"].append({"u": u, "p": request.form.get('p'), "ad": request.form.get('ad')})
        return redirect('/?msg=ok')

    elif aksiyon == "bakiye_iste" and session.get("user"):
        db["bakiye_talepleri"].append({"u": session["user"], "m": int(request.form.get('m', 0))})
        return redirect('/')

    if session.get("user") == "admin":
        if aksiyon == "onay" and id:
            b = db["basvurular"].pop(int(id))
            db["users"][b['u']] = {"pw": b['p'], "bakiye": 0, "ad": b['ad']}
        elif aksiyon == "bakiye_onay" and id:
            t = db["bakiye_talepleri"].pop(int(id))
            if t['u'] in db["users"]: db["users"][t['u']]["bakiye"] += t['m']

    elif aksiyon == "kupon_yap" and session.get("user"):
        u = session["user"]; misli = int(request.form.get('misli', 0))
        if db["users"][u]["bakiye"] >= misli:
            db["users"][u]["bakiye"] -= misli
            db["kuponlar"].insert(0, {"u": u, "misli": misli, "oran": float(request.form.get('toplam_oran', 1.0)), "durum": "Bekliyor... ⏱️", "detay": "Kupon", "baslangic_zamani": datetime.now(), "bitis_zamani": datetime.now() + timedelta(minutes=90), "tarih": datetime.now().strftime("%d.%m %H:%M")})
    
    return redirect('/')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9090))
    app.run(host='0.0.0.0', port=port)
