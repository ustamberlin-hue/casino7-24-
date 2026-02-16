import random
import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, redirect, request, session, jsonify

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
                k["durum"] = "LOST ❌"; k["kazanc"] = 0

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
        .odd-btn { background:#262a33; border:1px solid #333; color:#fcd535; padding:8px 2px; border-radius:6px; text-align:center; font-size:11px; cursor:pointer; }
        .odd-btn.selected { background:#fcd535; color:black; font-weight:bold; }
        .footer { position:fixed; bottom:0; width:100%; background:#16181c; display:flex; border-top:1px solid #333; z-index:100; }
        .f-btn { flex:1; text-align:center; padding:15px; color:white; text-decoration:none; font-size:11px; }
        .bet-slip { position:fixed; bottom:55px; width:100%; background:#fcd535; color:black; padding:12px; display:none; z-index:99; box-sizing:border-box; border-radius:15px 15px 0 0; }
        .horizontal-menu { display:flex; overflow-x:auto; padding:10px; gap:10px; white-space:nowrap; scrollbar-width: none; }
        .menu-item { background:#262a33; padding:8px 18px; border-radius:20px; font-size:12px; color:#fcd535; border:1px solid #333; cursor:pointer; }
        .menu-item.active { background:#fcd535; color:black; font-weight:bold; }

        /* CASINO STYLES */
        .slot-machine { display:flex; justify-content:center; gap:10px; margin:20px 0; }
        .reel { background:#000; border:3px solid #fcd535; width:80px; height:100px; display:flex; align-items:center; justify-content:center; font-size:40px; border-radius:10px; }
        .win-anim { animation: pulse 0.5s infinite; }
        @keyframes pulse { 0% { transform:scale(1); } 50% { transform:scale(1.1); background:#fcd535; } 100% { transform:scale(1); } }
    </style>
</head>
<body>
    <div class="header">🏢 GOKAYBETT HOLDİNG (EU)</div>

    {% if not session.user %}
        <div style="padding:30px;">
            {% if request.args.get('mod') == 'kayit' %}
                <h3 style="text-align:center;">Branch Application</h3>
                <form action="/islem/kayit" method="post">
                    <input type="text" name="ad" placeholder="Full Name" class="input" required>
                    <input type="text" name="u" placeholder="Username" class="input" required>
                    <input type="password" name="p" placeholder="Password" class="input" required>
                    <button class="btn">SEND APPLICATION</button>
                    <a href="/" style="color:#fcd535; display:block; text-align:center; margin-top:15px; text-decoration:none;">Back to Login</a>
                </form>
            {% else %}
                <h3 style="text-align:center;">Terminal Login</h3>
                <form action="/islem/giris" method="post">
                    <input type="text" name="u" placeholder="Username" class="input" required>
                    <input type="password" name="p" placeholder="Password" class="input" required>
                    <button class="btn">LOG IN</button>
                    <a href="/?mod=kayit" style="color:#fcd535; display:block; text-align:center; margin-top:15px; text-decoration:none;">Apply for Branch</a>
                </form>
            {% endif %}
        </div>
    {% else %}
        <div class="card" style="border-left:4px solid #0ecb81; display:flex; justify-content:space-between; align-items:center;">
            <b>BALANCE: <span id="user-balance" style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b>
            <button onclick="document.getElementById('bakiyeBox').style.display='block'" class="odd-btn">REQUEST €</button>
        </div>

        <div id="bakiyeBox" class="card" style="display:none; border:1px dashed #fcd535;">
            <form action="/islem/bakiye_iste" method="post">
                <input type="number" name="m" placeholder="Amount (€)" class="input" required>
                <button class="btn btn-green">SEND REQUEST</button>
                <button type="button" onclick="this.parentElement.parentElement.style.display='none'" class="btn btn-red" style="margin-top:5px; padding:5px;">Cancel</button>
            </form>
        </div>

        {% if page == 'BULTEN' %}
            <div class="horizontal-menu">
                <div class="menu-item active" onclick="filterBy('lig', 'all', this)">Tüm Ligler</div>
                {% for lig in ligler %}<div class="menu-item" onclick="filterBy('lig', '{{lig}}', this)">{{ lig }}</div>{% endfor %}
            </div>
            {% for m in bulten %}
                <div class="card match-card" data-lig="{{m.lig}}" data-gun="{{m.gun}}">
                    <div style="font-size:10px; color:#fcd535;">{{ m.lig }} | {{ m.tarih }} | {{ m.saat }}</div>
                    <div style="text-align:center; font-weight:bold;">{{ m.t1 }} vs {{ m.t2 }}</div>
                    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px; margin-top:10px;">
                        {% for k, v in m.oranlar.items() %}
                        <div class="odd-btn" onclick="sel(this, '{{m.id}}', '{{m.t1}} vs {{m.t2}}', '{{k}}', {{v}})">{{v}}</div>
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}

            <div id="slip" class="bet-slip">
                <form action="/islem/kupon_yap" method="post">
                    <input type="hidden" name="toplam_oran" id="totalO_input" value="1.00">
                    <input type="hidden" name="match_data" id="match_data_input">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <input type="number" name="misli" id="misli" value="100" min="1" style="width:70px;" oninput="calc()">
                        <b>WIN: <span id="win">0</span> €</b>
                        <button type="submit" class="btn" style="width:auto; padding:8px 15px;">BET</button>
                    </div>
                </form>
            </div>

        {% elif page == 'CASINO' %}
            <div class="card" style="text-align:center;">
                <h2 style="color:#fcd535;">GOKAY FRUIT 777</h2>
                <div class="slot-machine">
                    <div id="r1" class="reel">7️⃣</div>
                    <div id="r2" class="reel">7️⃣</div>
                    <div id="r3" class="reel">7️⃣</div>
                </div>
                <div style="margin:20px 0;">
                    <label>Bahis: </label>
                    <select id="slot-bet" class="input" style="width:100px; display:inline-block; margin:0;">
                        <option value="50">50 €</option>
                        <option value="100">100 €</option>
                        <option value="500">500 €</option>
                        <option value="1000">1000 €</option>
                    </select>
                </div>
                <button onclick="spinSlot()" id="spin-btn" class="btn">SPIN</button>
                <div id="casino-msg" style="margin-top:15px; font-weight:bold; height:20px;"></div>
            </div>

        {% elif page == 'KUPONLAR' %}
            <div style="padding:10px;">
                {% for k in db.kuponlar if k.u == session.user %}
                <div class="card">
                    <div style="font-size:11px; color:#888;">{{ k.tarih }} - {{ k.durum }}</div>
                    <div>{{ k.detay }}</div>
                    <b>{{ k.misli }}€ x {{ k.oran }}</b>
                </div>
                {% endfor %}
            </div>

        {% elif page == 'ADMIN' and session.user == 'admin' %}
            <div style="padding:10px;">
                <h3>Admin Panel</h3>
                {% for b in db.basvurular %}
                    <div class="card">
                        {{ b.ad }} (@{{ b.u }})
                        <a href="/islem/onay/{{ loop.index0 }}" class="btn btn-green">ONAY</a>
                    </div>
                {% endfor %}
            </div>
        {% endif %}

        <div class="footer">
            <a href="/p/BULTEN" class="f-btn">BÜLTEN</a>
            <a href="/p/CASINO" class="f-btn" style="color:#fcd535;">CASINO</a>
            <a href="/p/KUPONLAR" class="f-btn">KUPONLAR</a>
            {% if session.user == 'admin' %}<a href="/p/ADMIN" class="f-btn">YÖNETİM</a>{% endif %}
            <a href="/logout" class="f-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <script>
        function filterBy(type, val, el) {
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.match-card').forEach(c => {
                c.style.display = (val === 'all' || c.getAttribute('data-lig') === val) ? 'block' : 'none';
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
            let m = document.getElementById('misli').value;
            document.getElementById('win').innerText = Math.floor(o * m);
        }

        async function spinSlot() {
            const btn = document.getElementById('spin-btn');
            const bet = document.getElementById('slot-bet').value;
            btn.disabled = true;
            document.getElementById('casino-msg').innerText = "Dönüyor...";

            const res = await fetch('/islem/slot_spin', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `bet=${bet}`
            });
            const data = await res.json();

            if(data.error) {
                alert(data.error);
                btn.disabled = false;
                return;
            }

            // Basit Animasyon
            let count = 0;
            let timer = setInterval(() => {
                const symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"];
                document.getElementById('r1').innerText = symbols[Math.floor(Math.random()*5)];
                document.getElementById('r2').innerText = symbols[Math.floor(Math.random()*5)];
                document.getElementById('r3').innerText = symbols[Math.floor(Math.random()*5)];
                count++;
                if(count > 10) {
                    clearInterval(timer);
                    document.getElementById('r1').innerText = data.reel[0];
                    document.getElementById('r2').innerText = data.reel[1];
                    document.getElementById('r3').innerText = data.reel[2];
                    
                    document.getElementById('user-balance').innerText = data.new_balance + " €";
                    document.getElementById('casino-msg').innerText = data.win > 0 ? "KAZANDIN: " + data.win + "€ !" : "Kaybettin!";
                    if(data.win > 0) document.querySelectorAll('.reel').forEach(r => r.classList.add('win-anim'));
                    else document.querySelectorAll('.reel').forEach(r => r.classList.remove('win-anim'));
                    btn.disabled = false;
                }
            }, 100);
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
    return render_template_string(HTML, bakiye=u_data['bakiye'], bulten=aktif_bulten_getir(), session=session, page=page, fmt=format_euro, db=db, ligler=LIGLER)

@app.route('/islem/<aksiyon>', methods=['POST', 'GET'])
@app.route('/islem/<aksiyon>/<id>', methods=['POST', 'GET'])
def islem(aksiyon, id=None):
    if aksiyon == "giris":
        u, p = request.form.get('u', '').strip().lower(), request.form.get('p', '')
        if u in db["users"] and db["users"][u]["pw"] == p: 
            session["user"] = u
            return redirect('/')
    
    elif aksiyon == "slot_spin" and session.get("user"):
        u = session["user"]
        bet = int(request.form.get('bet', 0))
        if db["users"][u]["bakiye"] < bet: return jsonify({"error": "Yetersiz Bakiye"})
        
        db["users"][u]["bakiye"] -= bet
        win = 0
        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        
        # %50 Kazanma Oranı Ayarı
        if random.random() < 0.50:
            s = random.choice(symbols)
            reel = [s, s, s]
            win = bet * random.choice([2, 5, 10])
            db["users"][u]["bakiye"] += win
        else:
            reel = [random.choice(symbols) for _ in range(3)]
            if reel[0] == reel[1] == reel[2]: # Tesadüfen kazanırsa
                win = bet * 5; db["users"][u]["bakiye"] += win
        
        return jsonify({"reel": reel, "win": win, "new_balance": format_euro(db["users"][u]["bakiye"])})

    elif aksiyon == "kayit":
        db["basvurular"].append({"u": request.form.get('u'), "p": request.form.get('p'), "ad": request.form.get('ad')})
        return redirect('/?msg=ok')

    elif aksiyon == "onay" and session.get("user") == "admin":
        b = db["basvurular"].pop(int(id))
        db["users"][b['u']] = {"pw": b['p'], "bakiye": 0, "ad": b['ad']}
        return redirect('/p/ADMIN')

    elif aksiyon == "kupon_yap" and session.get("user"):
        u = session["user"]; misli = int(request.form.get('misli', 0))
        if db["users"][u]["bakiye"] >= misli:
            db["users"][u]["bakiye"] -= misli
            db["kuponlar"].insert(0, {"u": u, "misli": misli, "oran": float(request.form.get('toplam_oran')), "durum": "Bekliyor...", "detay": "Kupon", "tarih": "Bugün", "baslangic_zamani": datetime.now(), "bitis_zamani": datetime.now()})
        return redirect('/p/KUPONLAR')

    return redirect('/')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9090))
    app.run(host='0.0.0.0', port=port)
