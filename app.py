import requests
import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'casino_724_ultimate_secret_key'

# --- YARDIMCI FONKSİYONLAR ---

def oran_uret(mac_id):
    """Her maç için sabit ama rastgele görünen oranlar üretir"""
    random.seed(mac_id) # Aynı maç için hep aynı oran kalsın
    ms1 = round(random.uniform(1.20, 3.50), 2)
    msx = round(random.uniform(3.00, 4.50), 2)
    ms2 = round(random.uniform(1.80, 5.00), 2)
    return {"1": ms1, "X": msx, "2": ms2}

def tum_dunya_maclarini_getir():
    bugun = datetime.now().strftime('%Y-%m-%d')
    # Farklı kanallardan veri çekme
    urls = [
        f"https://www.thesportsdb.com/api/v1/json/1/eventsday.php?d={bugun}&s=Soccer",
        "https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id=4328", # Premier Lig
        "https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id=4422"  # Şampiyonlar Ligi
    ]
    
    etkinlikler = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            data = r.json().get('events', [])
            if data: etkinlikler.extend(data)
        except: continue
            
    # Tekilleştirme ve Oran Ekleme
    sonuc = {}
    for m in etkinlikler:
        if m['idEvent'] not in sonuc:
            m['oranlar'] = oran_uret(m['idEvent'])
            sonuc[m['idEvent']] = m
    return list(sonuc.values())

# --- YOLLAR (ROUTES) ---

@app.route('/')
def index():
    if 'bakiye' not in session:
        session['bakiye'] = 1000 # İlk giriş bonusu
    if 'kuponlar' not in session:
        session['kuponlar'] = []
        
    maclar = tum_dunya_maclarini_getir()
    return render_template_string(HTML_SABLONU, maclar=maclar, bakiye=session['bakiye'], kuponlar=session['kuponlar'])

@app.route('/oyna', methods=['POST'])
def oyna():
    mac_adi = request.form.get('mac_adi')
    tahmin = request.form.get('tahmin')
    oran = float(request.form.get('oran'))
    miktar = int(request.form.get('miktar', 0))
    
    if miktar > session['bakiye']:
        return "Yetersiz Bakiye!", 400
    
    # Bahsi işle
    session['bakiye'] -= miktar
    yeni_kupon = {
        "mac": mac_adi,
        "tahmin": tahmin,
        "oran": oran,
        "yatirilan": miktar,
        "durum": "Beklemede",
        "tarih": datetime.now().strftime('%H:%M:%S')
    }
    
    # Listeyi güncellemek için session'ı zorla
    kupon_listesi = session.get('kuponlar', [])
    kupon_listesi.insert(0, yeni_kupon)
    session['kuponlar'] = kupon_listesi
    session.modified = True
    
    return redirect(url_for('index'))

# --- DEV TASARIM (HTML) ---

HTML_SABLONU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | PROFESYONEL</title>
    <style>
        :root { --main-green: #00ff41; --dark-bg: #05070a; --card-bg: #12161f; }
        body { background: var(--dark-bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; }
        .header { background: #11141b; padding: 15px; text-align: center; border-bottom: 2px solid var(--main-green); sticky; top: 0; z-index: 100; }
        .bakiye-kart { background: var(--main-green); color: black; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 5px; }
        .container { padding: 10px; }
        .mac-kart { background: var(--card-bg); border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #232936; }
        .lig-adi { color: var(--main-green); font-size: 11px; text-transform: uppercase; }
        .takimlar { font-size: 16px; font-weight: bold; margin: 10px 0; display: block; }
        .oran-tablo { display: flex; gap: 5px; margin-bottom: 15px; }
        .oran-btn { background: #1c222d; border: 1px solid #343a40; color: white; padding: 10px; flex: 1; border-radius: 6px; cursor: pointer; text-align: center; }
        .oran-btn:hover { border-color: var(--main-green); color: var(--main-green); }
        .oran-btn b { display: block; font-size: 14px; }
        .oran-btn small { font-size: 10px; color: #888; }
        .bahis-form { display: flex; gap: 5px; background: #05070a; padding: 8px; border-radius: 8px; align-items: center; }
        input[type="number"] { background: transparent; border: none; color: white; width: 60px; outline: none; }
        .onay-btn { background: var(--main-green); color: black; border: none; padding: 10px; border-radius: 5px; font-weight: bold; flex-grow: 1; }
        .kuponlarim { margin-top: 30px; border-top: 1px solid #333; padding-top: 10px; }
        .kupon-tek { background: #11141b; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 12px; border-left: 3px solid #888; }
    </style>
</head>
<body>
    <div class="header">
        <div style="font-size: 20px; font-weight: 900;">CASINO <span style="color:var(--main-green)">7-24</span></div>
        <div class="bakiye-kart">CÜZDAN: {{ bakiye }} TL</div>
    </div>

    <div class="container">
        <h3>⚽ CANLI BÜLTEN</h3>
        {% for mac in maclar %}
        <div class="mac-kart">
            <span class="lig-adi">{{ mac.strLeague }}</span>
            <span class="takimlar">{{ mac.strEvent }}</span>
            
            <form action="/oyna" method="post">
                <input type="hidden" name="mac_adi" value="{{ mac.strEvent }}">
                <div class="oran-tablo">
                    <label class="oran-btn">
                        <input type="radio" name="tahmin" value="MS 1" required style="display:none">
                        <input type="hidden" name="oran" value="{{ mac.oranlar['1'] }}">
                        <small>MS 1</small><b>{{ mac.oranlar['1'] }}</b>
                    </label>
                    <label class="oran-btn">
                        <input type="radio" name="tahmin" value="MS X" style="display:none">
                        <small>MS X</small><b>{{ mac.oranlar['X'] }}</b>
                    </label>
                    <label class="oran-btn">
                        <input type="radio" name="tahmin" value="MS 2" style="display:none">
                        <small>MS 2</small><b>{{ mac.oranlar['2'] }}</b>
                    </label>
                </div>
                <div class="bahis-form">
                    <span>Miktar:</span>
                    <input type="number" name="miktar" value="100" min="10">
                    <button type="submit" class="onay-btn">KUPONU YATIR</button>
                </div>
            </form>
        </div>
        {% endfor %}

        <div class="kuponlarim">
            <h4>📋 SON KUPONLARIM</h4>
            {% for kupon in kuponlar %}
            <div class="kupon-tek">
                <b>{{ kupon.mac }}</b> | Tahmin: {{ kupon.tahmin }} ({{ kupon.oran }})<br>
                Yatırılan: {{ kupon.yatirilan }} TL | Durum: <span style="color:orange">{{ kupon.durum }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
