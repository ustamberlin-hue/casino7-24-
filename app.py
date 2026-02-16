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
        if k["durum"] in ["WINNER ✅", "LOST ❌", "İPTAL EDİLDİ ↩️"]: continue
        bitis_vakti = k["bitis_zamani"] + timedelta(minutes=95)
        if simdi < k["baslangic_zamani"]: k["durum"] = "Bekliyor... ⏱️"
        elif k["baslangic_zamani"] <= simdi <= bitis_vakti: k["durum"] = "Canlıda... ⚽"
        elif simdi > bitis_vakti:
            kazandi = random.random() < 0.3
            if kazandi:
                k["durum"] = "WINNER ✅"
                k["kazanc"] = int(k["misli"] * k["oran"])
                if k["u"] in db["users"]: db["users"][k["u"]]["bakiye"] += k["kazanc"]
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
        
        /* CASINO UI */
        .game-tabs { display:flex; gap:5px; padding:10px; }
        .tab-btn { flex:1; padding:10px; background:#262a33; color:#fcd535; border:1px solid #444; border-radius:8px; font-size:10px; }
        .tab-btn.active { background:#fcd535; color:black; font-weight:bold; }
        .reels { display:flex; justify-content:center; gap:8px; margin:20px 0; }
        .slot-reel { background:linear-gradient(180deg, #000, #222); border:2px solid #fcd535; height:80px; width:65px; display:flex; align-items:center; justify-content:center; font-size:35px; border-radius:12px; }
        .winning { animation: blink 0.3s infinite; border-color: #0ecb81; }
        @keyframes blink { 0% { opacity:1; } 50% { opacity:0.6; } 100% { opacity:1; } }
    </style>
</head>
<body>
    <div class="header">🏢 GOKAYBETT HOLDİNG (EU)</div>

    {% if not session.user %}
        <div style="padding:30px;">
            <form action="/islem/giris" method="post">
                <input type="text" name="u" placeholder="Username" class="input" required>
                <input type="password" name="p" placeholder="Password" class="input" required>
                <button class="btn">LOG IN</button>
            </form>
        </div>
    {% else %}
        {% if page == 'BULTEN' %}
            <div class="card">
                <b>BALANCE: <span id="top-balance" style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b>
            </div>
            {% for m in bulten %}
                <div class="card">
                    <div style="font-size:10px; color:#fcd535;">{{ m.lig }}</div>
                    <div style="text-align:center;">{{ m.t1 }} vs {{ m.t2 }}</div>
                </div>
            {% endfor %}

        {% elif page == 'CASINO' %}
            <div class="game-tabs">
                <button class="tab-btn active" onclick="switchGame('classic', this)">GOKAY CLASSIC</button>
                <button class="tab-btn" onclick="switchGame('wild', this)">WILD FIRE 🔥</button>
                <button class="tab-btn" onclick="switchGame('deluxe', this)">FRUIT DELUXE 💎</button>
            </div>

            <div class="card" style="text-align:center;">
                <h3 id="game-title" style="color:#fcd535;">🎰 GOKAY CLASSIC</h3>
                <div class="reels">
                    <div id="reel1" class="slot-reel">🍒</div>
                    <div id="reel2" class="slot-reel">🍋</div>
                    <div id="reel3" class="slot-reel">7️⃣</div>
                </div>
                
                <div style="margin-bottom:15px;">
                    <b>Bakiye: <span id="slot-balance" style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b><br><br>
                    <select id="slot-bet" class="input" style="width:140px; display:inline-block;">
                        <option value="0.5">0.50 €</option><option value="1">1.00 €</option>
                        <option value="2">2.00 €</option><option value="3">3.00 €</option>
                        <option value="5">5.00 €</option><option value="7">7.00 €</option>
                        <option value="10">10.00 €</option>
                    </select>
                </div>
                
                <button onclick="spin()" id="spin-btn" class="btn">SPIN (ÇEVİR)</button>
                <p id="slot-res" style="margin-top:15px; font-weight:bold; min-height:22px;"></p>
            </div>
        {% endif %}

        <div class="footer">
            <a href="/p/BULTEN" class="f-btn">BÜLTEN</a>
            <a href="/p/CASINO" class="f-btn" style="color:#fcd535;">CASINO</a>
            <a href="/logout" class="f-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <script>
        let selectedGame = 'classic';
        function switchGame(game, btn) {
            selectedGame = game;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('game-title').innerText = game.toUpperCase() + " SLOT";
        }

        async function spin() {
            const btn = document.getElementById('spin-btn');
            const bet = document.getElementById('slot-bet').value;
            const resText = document.getElementById('slot-res');
            
            btn.disabled = true;
            resText.innerText = "🌀 DÖNÜYOR...";
            document.querySelectorAll('.slot-reel').forEach(r => r.classList.remove('winning'));
            
            try {
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

                // Animasyon
                let counter = 0;
                const syms = ["🍒", "🍋", "🔔", "🍉", "🍇", "💎", "7️⃣"];
                const interval = setInterval(() => {
                    document.getElementById('reel1').innerText = syms[Math.floor(Math.random()*7)];
                    document.getElementById('reel2').innerText = syms[Math.floor(Math.random()*7)];
                    document.getElementById('reel3').innerText = syms[Math.floor(Math.random()*7)];
                    counter++;
                    if(counter > 15) {
                        clearInterval(interval);
                        document.getElementById('reel1').innerText = data.reels[0];
                        document.getElementById('reel2').innerText = data.reels[1];
                        document.getElementById('reel3').innerText = data.reels[2];
                        
                        // Bakiyeyi güncelle
                        const newBal = data.new_balance + " €";
                        if(document.getElementById('slot-balance')) document.getElementById('slot-balance').innerText = newBal;
                        if(document.getElementById('top-balance')) document.getElementById('top-balance').innerText = newBal;
                        
                        if(data.win > 0) {
                            resText.innerText = "💰 KAZANDIN: " + data.win + " €";
                            resText.style.color = "#0ecb81";
                            document.querySelectorAll('.slot-reel').forEach(r => r.classList.add('winning'));
                        } else {
                            resText.innerText = "❌ KAYBETTİN";
                            resText.style.color = "#ff4444";
                        }
                        btn.disabled = false;
                    }
                }, 70);
            } catch(e) {
                btn.disabled = false;
                resText.innerText = "Hata oluştu!";
            }
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
    return render_template_string(HTML, bakiye=u_data['bakiye'], bulten=aktif_bulten_getir()[:5], session=session, page=page, fmt=format_euro)

@app.route('/islem/<aksiyon>', methods=['POST', 'GET'])
def islem(aksiyon):
    if aksiyon == "giris":
        u, p = request.form.get('u', '').strip().lower(), request.form.get('p', '')
        if u in db["users"] and db["users"][u]["pw"] == p: 
            session["user"] = u
        return redirect('/')

    elif aksiyon == "slot_spin" and session.get("user"):
        u = session["user"]
        bet = float(request.form.get('bet', 0))
        
        if db["users"][u]["bakiye"] < bet:
            return jsonify({"error": "Bakiye yetersiz!"})
        
        # Bakiyeyi düş
        db["users"][u]["bakiye"] -= bet
        
        # PATRON AYARI: %70 KASA / %30 OYUNCU
        is_win = random.random() < 0.30
        win_amt = 0
        symbols = ["🍒", "🍋", "🔔", "🍉", "🍇", "💎", "7️⃣"]
        
        if is_win:
            s = random.choice(symbols)
            reels = [s, s, s]
            win_amt = float(bet * random.choice([2, 5, 10]))
            db["users"][u]["bakiye"] += win_amt
        else:
            reels = random.sample(symbols, 3)

        return jsonify({
            "reels": reels, 
            "win": win_amt, 
            "new_balance": format_euro(db["users"][u]["bakiye"])
        })

    return redirect('/')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 9090)))
