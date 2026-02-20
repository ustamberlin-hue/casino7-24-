import requests
import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'casino_724_unlimited_leagues_99'

# --- DEV VERİ MOTORU ---

def oran_uret(mac_id):
    random.seed(mac_id)
    return {
        "1": round(random.uniform(1.20, 5.00), 2),
        "X": round(random.uniform(3.10, 5.50), 2),
        "2": round(random.uniform(1.90, 9.00), 2)
    }

def tum_dunya_bultenini_getir():
    # 1. ADIM: Sisteme kayıtlı TÜM liglerin listesini çek
    ligler_url = "https://www.thesportsdb.com/api/v1/json/1/all_leagues.php"
    bulten = []
    
    try:
        r_ligler = requests.get(ligler_url, timeout=5)
        tum_ligler = r_ligler.json().get('leagues', [])
        
        # 2. ADIM: Sadece Futbol olanları ayıkla ve maçlarını tara
        # Not: Ücretsiz API hız limiti nedeniyle en popüler ve aktif ilk 50 ligi tarar
        sayac = 0
        for lig in tum_ligler:
            if lig['strSport'] == 'Soccer' and sayac < 50:
                lig_id = lig['idLeague']
                lig_ad = lig['strLeague']
                
                # Her ligin sıradaki maçlarını çek
                mac_url = f"https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id={lig_id}"
                try:
                    r_maclar = requests.get(mac_url, timeout=2)
                    data = r_maclar.json().get('events', [])
                    if data:
                        for mac in data:
                            mac['oranlar'] = oran_uret(mac['idEvent'])
                            mac['lig_adi'] = lig_ad
                            bulten.append(mac)
                        sayac += 1 # Sadece içinde maç olan ligleri say
                except:
                    continue
    except:
        return []
            
    # Tüm dünyayı tarih sırasına diz
    bulten.sort(key=lambda x: (x.get('dateEvent', ''), x.get('strTime', '')))
    return bulten

# --- ROUTER VE MANTIK ---

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    if 'kuponlar' not in session: session['kuponlar'] = []
    
    maclar = tum_dunya_bultenini_getir()
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

# --- TASARIM (DEV BÜLTEN) ---

HTML_SABLONU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casino 7-24 | Global Dev Bülten</title>
    <style>
        body { background: #05070a; color: white; font-family: sans-serif; margin: 0; padding: 5px; }
        .top-nav { background: #11141b; padding: 15px; text-align: center; border-bottom: 2px solid #00ff41; position: sticky; top: 0; z-index: 100; }
        .bakiye-box { background: #00ff41; color: black; padding: 8px 15px; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px; }
        .lig-ayirici { background: #1c1f26; color: #00ff41; padding: 5px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-top: 15px; display: inline-block; border-left: 3px solid #00ff41; }
        .mac-kart { background: #12161f; border-radius: 10px; padding: 12px; margin-top: 8px; border: 1px solid #232936; }
        .takim-text { font-size: 15px; font-weight: bold; display: block; margin-bottom: 10px; }
        .oran-grid { display: flex; gap: 5px; }
        .oran-item { flex: 1; background: #232936; border: 1px solid #343a40; padding: 8px; border-radius: 6px; text-align: center; cursor: pointer; }
        input[type="radio"] { display: none; }
        input[type="radio"]:checked + .val { background: #00ff41; color: black; font-weight: bold; border-radius: 3px; padding: 2px; }
        .alt-bar { display: flex; margin-top: 12px; gap: 5px; }
        .m-in { background: #000; border: 1px solid #333; color: white; width: 60px; padding: 8px; border-radius: 4px; }
        .btn-submit { background: #00ff41; color: black; border: none; flex: 1; border-radius: 4px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="top-nav">
        <div style="font-size: 18px; font-weight: 800;">CASINO 7-24 GLOBAL</div>
        <div class="bakiye-box">💰 {{ bakiye }} TL</div>
    </div>

    {% if not maclar %}
    <p style="text-align:center; color:#666; margin-top:50px;">Dünya ligleri taranıyor...<br>Lütfen 10 saniye sonra sayfayı yenileyin.</p>
    {% endif %}

    {% for mac in maclar %}
    <div class="lig-ayirici">{{ mac.lig_adi }}</div>
    <div class="mac-kart">
        <div style="font-size: 10px; color: #555;">{{ mac.dateEvent }} | {{ mac.strTime }}</div>
        <span class="takim-text">{{ mac.strEvent }}</span>
        
        <form action="/oyna" method="post">
            <input type="hidden" name="mac_adi" value="{{ mac.strEvent }}">
            <div class="oran-grid">
                <label class="oran-item">
                    <input type="radio" name="tahmin" value="MS 1" required>
                    <div class="val">1<br>{{ mac.oranlar['1'] }}</div>
                    <input type="hidden" name="oran" value="{{ mac.oranlar['1'] }}">
                </label>
                <label class="oran-item">
                    <input type="radio" name="tahmin" value="MS X">
                    <div class="val">X<br>{{ mac.oranlar['X'] }}</div>
                </label>
                <label class="oran-item">
                    <input type="radio" name="tahmin" value="MS 2">
                    <div class="val">2<br>{{ mac.oranlar['2'] }}</div>
                </label>
            </div>
            <div class="alt-bar">
                <input type="number" name="miktar" value="100" class="m-in">
                <button type="submit" class="btn-submit">Oyna</button>
            </div>
        </form>
    </div>
    {% endfor %}
</body>
</html>
