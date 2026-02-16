import random
import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, redirect, request, session, url_for

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
            <div class="horizontal-menu">
                <div class="menu-item active" onclick="filterBy('gun', 'all', this)">Tüm Günler</div>
                {% for gun in gunler_liste %}<div class="menu-item" onclick="filterBy('gun', '{{gun}}', this)">{{ gun }}</div>{% endfor %}
            </div>

            <div class="card" style="border-left:4px solid #0ecb81; display:flex; justify-content:space-between; align-items:center;">
                <b>BALANCE: <span style="color:#0ecb81;">{{ fmt(bakiye) }} €</span></b>
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

        {% elif page == 'SETTINGS' %}
            <div class="card">
                <h3>Account Settings</h3>
                {% if request.args.get('msg') == 'pwok' %}<div class="error-msg" style="background:#0ecb81;">Password Updated!</div>{% endif %}
                <form action="/islem/sifre_degistir" method="post">
                    <label style="font-size:12px; color:#888;">New Password</label>
                    <input type="password" name="p" placeholder="Min 4 characters" class="input" required>
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

                <h4>Users List</h4>
                {% for u, d in db.users.items() %}
                    {% if u != 'admin' %}
                    <div class="card" style="display:flex; justify-content:space-between;">
                        <span>{{ d.ad }} ({{ fmt(d.bakiye) }}€)</span>
                        <a href="/islem/sil/{{ u }}" style="color:red; font-size:12px;">REMOVE</a>
                    </div>
                    {% endif %}
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
                        <div style="text-align:right;">
                            <span style="display:block; font-weight:bold; color:{% if 'WINNER' in k.durum %}#0ecb81{% elif 'LOST' in k.durum %}#ff4444{% elif 'İPTAL' in k.durum %}#888{% else %}#fcd535{% endif %};">{{ k.durum }}</span>
                            {% if k.durum == 'Bekliyor... ⏱️' %}
                            <a href="/islem/kupon_iptal/{{ loop.index0 }}" style="background:#ff4444; color:white; font-size:10px; padding:4px 8px; border-radius:4px; text-decoration:none; display:inline-block; margin-top:5px;">İPTAL ET</a>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% endif %}

        <div class="footer">
            <a href="/p/BULTEN" class="f-btn">BÜLTEN</a>
            <a href="/p/KUPONLAR" class="f-btn">KUPONLAR</a>
            <a href="/p/SETTINGS" class="f-btn">AYARLAR</a>
            {% if session.user == 'admin' %}<a href="/p/ADMIN" class="f-btn" style="color:#fcd535;">YÖNETİM</a>{% endif %}
            <a href="/logout" class="f-btn" style="color:red;">ÇIKIŞ</a>
        </div>
    {% endif %}

    <script>
        let currentLig = 'all'; let currentGun = 'all';
        function filterBy(type, value, el) {
            el.parentElement.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            el.classList.add('active');
            if(type === 'lig') currentLig = value;
            if(type === 'gun') currentGun = value;
            document.querySelectorAll('.match-card').forEach(card => {
                const lM = (currentLig === 'all' || card.getAttribute('data-lig') === currentLig);
                const gM = (currentGun === 'all' || card.getAttribute('data-gun') === currentGun);
                card.style.display = (lM && gM) ? 'block' : 'none';
            });
        }
        let picks = [];
        function sel(el, id, teams, pick, odd) {
            let card = el.closest('.card');
            let buttons = card.querySelectorAll('.odd-btn');
            if(el.classList.contains('selected')) {
                el.classList.remove('selected');
                picks = picks.filter(x => x.id !== id);
            } else {
                buttons.forEach(b => b.classList.remove('selected'));
                picks = picks.filter(x => x.id !== id);
                el.classList.add('selected');
                picks.push({id, teams, pick, odd});
            }
            document.getElementById('slip').style.display = picks.length > 0 ? 'block' : 'none';
            document.getElementById('match_data_input').value = JSON.stringify(picks);
            calc();
        }
        function calc() {
            let o = picks.reduce((acc, c) => acc * c.odd, 1);
            let m = document.getElementById('misli').value || 0;
            document.getElementById('totalO_input').value = o.toFixed(2);
            document.getElementById('win').innerText = Math.floor(o * m).toLocaleString('de-DE');
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

    elif aksiyon == "kayit":
        u = request.form.get('u', '').strip().lower()
        if u in db["users"] or any(b['u'] == u for b in db["basvurular"]): 
            return redirect('/?mod=kayit&hata=isim')
        db["basvurular"].append({"u": u, "p": request.form.get('p'), "ad": request.form.get('ad')})
        return redirect('/?msg=ok')

    elif aksiyon == "sifre_degistir" and session.get("user"):
        new_pw = request.form.get('p')
        if new_pw:
            db["users"][session["user"]]["pw"] = new_pw
            return redirect('/p/SETTINGS?msg=pwok')

    elif aksiyon == "bakiye_iste" and session.get("user"):
        db["bakiye_talepleri"].append({"u": session["user"], "m": int(request.form.get('m', 0))})
        return redirect('/')

    if session.get("user") == "admin":
        if aksiyon == "onay" and id:
            b = db["basvurular"].pop(int(id))
            db["users"][b['u']] = {"pw": b['p'], "bakiye": 0, "ad": b['ad']}
        elif aksiyon == "red" and id:
            db["basvurular"].pop(int(id))
        elif aksiyon == "bakiye_onay" and id:
            t = db["bakiye_talepleri"].pop(int(id))
            if t['u'] in db["users"]: db["users"][t['u']]["bakiye"] += t['m']
        elif aksiyon == "bakiye_iptal" and id:
            db["bakiye_talepleri"].pop(int(id))
        elif aksiyon == "sil" and id:
            db["users"].pop(id, None)

    if aksiyon == "kupon_iptal" and session.get("user") and id:
        k = db["kuponlar"][int(id)]
        if k["u"] == session["user"] and datetime.now() < k["baslangic_zamani"] and k["durum"] == "Bekliyor... ⏱️":
            db["users"][k["u"]]["bakiye"] += k["misli"]
            k["durum"] = "İPTAL EDİLDİ ↩️"
        return redirect('/p/KUPONLAR')

    if aksiyon == "kupon_yap" and session.get("user"):
        u = session["user"]
        misli = int(request.form.get('misli', 0))
        oran = float(request.form.get('toplam_oran', 1.0))
        picks = json.loads(request.form.get('match_data', '[]'))
        if misli > 0 and db["users"][u]["bakiye"] >= misli:
            ilk_m = datetime.max; son_m = datetime.min; det = []
            for p in picks:
                mac = next((m for m in TUM_BULTEN_HAVUZU if m['id'] == p['id']), None)
                if mac:
                    det.append(f"{mac['t1']}-{mac['t2']} ({p['pick']})")
                    ilk_m = min(ilk_m, mac['tam_zaman']); son_m = max(son_m, mac['tam_zaman'])
            db["users"][u]["bakiye"] -= misli
            db["kuponlar"].insert(0, {"u": u, "misli": misli, "oran": oran, "durum": "Bekliyor... ⏱️", "detay": " / ".join(det), "baslangic_zamani": ilk_m, "bitis_zamani": son_m, "tarih": datetime.now().strftime("%d.%m %H:%M")})
            return redirect('/p/KUPONLAR')
    return redirect('/')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    # Render'ın beklediği dinamik port ayarı
    port = int(os.environ.get("PORT", 9090))
    app.run(host='0.0.0.0', port=port)
