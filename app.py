import requests
import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'casino_724_fixed_v99'

# --- VERİ ÇEKME MOTORU ---
def dunya_bultenini_tara():
    # En stabil ve popüler ligleri seçtik (API limitine takılmamak için)
    ligler = {
        "Süper Lig": "4391", "Premier Lig": "4328", 
        "La Liga": "4335", "Serie A": "4332", 
        "Bundesliga": "4331", "Ligue 1": "4334",
        "Şampiyonlar Ligi": "4422", "Avrupa Ligi": "4423"
    }
    havuz = []
    for lig_ad, lig_id in ligler.items():
        url = f"https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id={lig_id}"
        try:
            r = requests.get(url, timeout=5)
            data = r.json().get('events', [])
            if data:
                for m in data:
                    random.seed(m['idEvent'])
                    m['oranlar'] = {
                        "1": round(random.uniform(1.40, 3.50), 2),
                        "X": round(random.uniform(3.10, 4.50), 2),
                        "2": round(random.uniform(2.10, 5.50), 2)
                    }
                    m['lig_adi'] = lig_ad
                    havuz.append(m)
        except:
            continue
    
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
    
    if miktar > session['bakiye']: return "Yetersiz Bakiye!", 400
    
    session['bakiye'] -= miktar
    session['kuponlar'].insert(0, {
        "mac": mac_adi, "tahmin": tahmin, "oran": oran,
        "yatirilan": miktar, "tarih": datetime.now().strftime('%H:%M')
    })
    session.modified = True
    return redirect(url_for('index'))

# --- TASARIM VE KAPANIŞ ---
HTML_SABLONU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: sans-serif; margin: 0; padding: 10px; }
        .header { background: #161b22; padding: 20px; border-radius: 15px; border-bottom: 4px solid #00ff41; text-align: center; margin-bottom: 20px; }
        .bakiye-tag { background: #00ff41; color: black; padding: 10px 20px; border-radius: 50px; font-weight: bold; font-size: 18px; display: inline-block; }
        .mac-kart { background: #161b22; border-radius: 12px; padding: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
        .lig-tag { background: #21262d; color: #00ff41; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .oran-btn { flex: 1; background: #21262d; border: 1px solid #30363d; color: white; padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; }
        .btn-bet { background: #00ff41; color: black; border: none; width: 100%; border-radius: 8px; padding: 12px; font-weight: bold; margin-top: 10px; cursor: pointer; }
        input[type="number"] { background: #000; border: 1px solid #30363d; color: white; width: 60px; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div style="font-size: 24px; font-weight: 800; color: #00ff41;">CASINO 7-24</div>
        <div class="bakiye-tag">💰 {{ bakiye }} TL</div>
    </div>

    {% if not maclar %}
    <div style="text-align:center; padding:50px; color:#888;">Veriler güncelleniyor, lütfen 5 saniye sonra sayfayı yenileyin...</div>
    {% endif %}

    {% for mac in maclar %}
    <div class="mac-kart">
        <span class="lig-tag">{{ mac.lig_adi }}</span>
        <div style="margin: 10px 0; font-weight: bold; font-size: 16px;">{{ mac.strEvent }}</div>
        <form action="/oyna" method="post">
            <input type="hidden" name="mac_adi" value="{{ mac.strEvent }}">
            <div style="display: flex; gap: 5px;">
                <label class="oran-btn"><input type="radio" name="tahmin" value="1" required> 1<br>{{ mac.oranlar['1'] }}<input type="hidden" name="oran" value="{{ mac.oranlar['1'] }}"></label>
                <label class="oran-btn"><input type="radio" name="tahmin" value="X"> X<br>{{ mac.oranlar['X'] }}</label>
                <label class="oran-btn"><input type="radio" name="tahmin" value="2"> 2<br>{{ mac.oranlar['2'] }}</label>
            </div>
            <div style="margin-top:10px; display:flex; gap:10px; align-items:center;">
                <input type="number" name="miktar" value="100" min="10">
                <button type="submit" class="btn-bet">BAHİS YAP</button>
            </div>
        </form>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    # Render için port ayarı
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
