import requests
import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'casino_724_ultimate_global_final'

# --- 10+ GLOBAL VERİ KAYNAĞI TARAMA ---
def dunya_bultenini_tara():
    ligler = {
        "🇹🇷 Süper Lig": "4391", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier Lig": "4328", 
        "🇪🇸 La Liga": "4335", "🇮🇹 Serie A": "4332", 
        "🇩🇪 Bundesliga": "4331", "🇫🇷 Ligue 1": "4334",
        "🇪🇺 Şampiyonlar Ligi": "4422", "🇪🇺 Avrupa Ligi": "4423",
        "🇳🇱 Eredivisie": "4337", "🇵🇹 Portekiz": "4344"
    }
    havuz = []
    for lig_ad, lig_id in ligler.items():
        url = f"https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id={lig_id}"
        try:
            r = requests.get(url, timeout=3)
            data = r.json().get('events', [])
            if data:
                for m in data:
                    random.seed(m['idEvent'])
                    m['oranlar'] = {"1": round(random.uniform(1.40, 4.20), 2), "X": round(random.uniform(3.10, 4.80), 2), "2": round(random.uniform(2.10, 6.50), 2)}
                    m['lig_adi'] = lig_ad
                    havuz.append(m)
        except: continue
    havuz.sort(key=lambda x: (x.get('dateEvent', ''), x.get('strTime', '')))
    return havuz

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    if 'kuponlar' not in session: session['kuponlar'] = []
    maclar = dunya_bultenini_tara()
    return render_template_string(HTML_SABLONU, maclar=maclar, bakiye=session['bakiye'], kuponlar=session['kuponlar'])

@app.route('/oyna', methods=['POST'])
def oyna():
    mac_adi = request.form.get('mac_adi')
    tahmin = request.form.get('tahmin')
    oran = request.form.get('oran')
    miktar = int(request.form.get('miktar', 0))
    if miktar > session['bakiye']: return "Bakiye Yetersiz!", 400
    session['bakiye'] -= miktar
    session['kuponlar'].insert(0, {"mac": mac_adi, "tahmin": tahmin, "oran": oran, "yatirilan": miktar, "tarih": datetime.now().strftime('%H:%M')})
    session.modified = True
    return redirect(url_for('index'))

# --- TASARIM KATMANI ---
HTML_SABLONU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | GLOBAL BÜLTEN</title>
    <style>
        body { background: #05070a; color: white; font-family: sans-serif; margin: 0; padding: 10px; }
        .header { background: #11141b; padding: 15px; border-radius: 12px; border-bottom: 3px solid #00ff41; text-align: center; margin-bottom: 20px; }
        .bakiye { color: #00ff41; font-size: 22px; font-weight: bold; }
        .mac-kart { background: #12161f; border-radius: 10px; padding: 15px; border: 1px solid #232936; margin-bottom: 15px; }
        .lig-adi { color: #00ff41; font-size: 11px; font-weight: bold; }
        .btn-oran { flex: 1; background: #232936; border: 1px solid #343a40; color: white; padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; }
        .btn-oyna { background: #00ff41; color: black; border: none; width: 100%; border-radius: 8px; padding: 12px; font-weight: bold; margin-top: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <div style="font-size: 20px; font-weight: 800;">CASINO 7-24</div>
        <div class="bakiye">💰 {{ bakiye }} TL</div>
    </div>
    {% for mac in maclar %}
    <div class="mac-kart">
        <div class="lig-adi">{{ mac.lig_adi }}</div>
        <div style="margin: 8px 0; font-weight: bold;">{{ mac.strEvent }}</div>
        <form action="/oyna" method="post">
            <input type="hidden" name="mac_adi" value="{{ mac.strEvent }}">
            <div style="display: flex; gap: 5px;">
                <label class="btn-oran"><input type="radio" name="tahmin" value="1" required> 1<br>{{ mac.oranlar['1'] }}<input type="hidden" name="oran" value="{{ mac.oranlar['1'] }}"></label>
                <label class="btn-oran"><input type="radio" name="tahmin" value="X"> X<br>{{ mac.oranlar['X'] }}</label>
                <label class="btn-oran"><input type="radio" name="tahmin" value="2"> 2<br>{{ mac.oranlar['2'] }}</label>
            </div>
            <div style="margin-top:10px; display:flex; gap:10px;">
                <input type="number" name="miktar" value="100" style="background:#000; color:white; border:1px solid #333; width:60px; border-radius:5px; padding:5px;">
                <button type="submit" class="btn-oyna">BAHİS YAP</button>
            </div>
        </form>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
