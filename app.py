import requests
import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'casino_724_ultimate_final_system'

# --- VERİ MOTORU (DÜNYADAKİ TÜM LİGLER) ---

def bulten_topla():
    # Adım 1: Tüm aktif ligleri öğren
    ligler_url = "https://www.thesportsdb.com/api/v1/json/1/all_leagues.php"
    bulten = []
    
    try:
        r_ligler = requests.get(ligler_url, timeout=5)
        tum_ligler = r_ligler.json().get('leagues', [])
        
        lig_sayac = 0
        for lig in tum_ligler:
            # Sadece futbol liglerini al ve Render'ı kasmamak için en aktif 50 ligle sınırla
            if lig['strSport'] == 'Soccer' and lig_sayac < 50:
                lig_id = lig['idLeague']
                lig_ad = lig['strLeague']
                
                # Her ligin 'Oynamayan / Gelecek' maçlarını çek
                mac_url = f"https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id={lig_id}"
                try:
                    r_maclar = requests.get(mac_url, timeout=2)
                    etkinlikler = r_maclar.json().get('events', [])
                    if etkinlikler:
                        for m in etkinlikler:
                            # Sabit oran üretimi
                            random.seed(m['idEvent'])
                            m['oranlar'] = {
                                "1": round(random.uniform(1.20, 4.00), 2),
                                "X": round(random.uniform(3.00, 5.00), 2),
                                "2": round(random.uniform(1.80, 7.00), 2)
                            }
                            m['lig_adi'] = lig_ad
                            bulten.append(m)
                        lig_sayac += 1
                except:
                    continue
    except:
        return []
            
    # Bülteni tarihe göre sırala
    bulten.sort(key=lambda x: (x.get('dateEvent', ''), x.get('strTime', '')))
    return bulten

# --- YOLLAR ---

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    if 'kuponlar' not in session: session['kuponlar'] = []
    
    maclar = bulten_topla()
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
        "yatirilan": miktar, "tarih": datetime.now().strftime('%d.%m %H:%M')
    })
    session.modified = True
    return redirect(url_for('index'))

# --- TASARIM (HATASIZ VE TAM) ---

HTML_SABLONU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casino 7-24 | Dev Dünya Bülteni</title>
    <style>
        body { background: #05070a; color: white; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
        .ust-panel { background: #11141b; padding: 15px; border-radius: 12px; border-bottom: 3px solid #00ff41; position: sticky; top: 0; z-index: 100; text-align: center; }
        .bakiye { color: #00ff41; font-size: 22px; font-weight: bold; margin-top: 5px; }
        .lig-ayirici { background: #1c1f26; color: #00ff41; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; margin: 20px 0 10px 0; border-left: 4px solid #00ff41; display: inline-block; }
        .mac-kart { background: #12161f; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #232936; }
        .takimlar { font-size: 17px; font-weight: bold; display: block; margin-bottom: 12px; }
        .oran-container { display: flex; gap: 8px; }
        .oran-btn { flex: 1; background: #232936; border: 1px solid #343a40; color: white; padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; transition: 0.2s; }
        .oran-btn:hover { border-color: #00ff41; }
        input[type="radio"] { display: none; }
        input[type="radio"]:checked + .oran-txt { background: #00ff41; color: black; font-weight: bold; padding: 2px 5px; border-radius: 4px; }
        .islem-alani { display: flex; gap: 8px; margin-top: 15px; }
        .m-input { background: #000; border: 1px solid #333; color: white; width: 75px; padding: 10px; border-radius: 6px; }
        .submit-btn { background: #00ff41; color: black; border: none; flex: 1; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .gecmis { margin-top: 40px; border-top: 1px solid #333; padding-top: 20px; }
        .kupon { background: #11141b; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #00ff41; font-size: 13px; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <div style="font-size: 20px; font-weight: 900;">CASINO 7-24</div>
        <div class="bakiye">💰 CÜZDAN: {{ bakiye }} TL</div>
    </div>

    {% for mac in maclar %}
    <span class="lig-ayirici">{{ mac.lig_adi }}</span>
    <div class="mac-kart">
        <div style="font-size: 11px; color: #666; margin-bottom: 5px;">📅 {{ mac.dateEvent }} | 🕒 {{ mac.strTime }}</div>
        <span class="takimlar">{{ mac.strEvent }}</span>
        
        <form action="/oyna" method="post">
            <input type="hidden" name="mac_adi" value="{{ mac.strEvent }}">
            <div class="oran-container">
                <label class="oran-btn">
                    <input type="radio" name="tahmin" value="MS 1" required>
                    <div class="oran-txt">1<br>{{ mac.oranlar['1'] }}</div>
                    <input type="hidden" name="oran" value="{{ mac.oranlar['1'] }}">
                </label>
                <label class="oran-btn">
                    <input type="radio" name="tahmin" value="MS X">
                    <div class="oran-txt">X<br>{{ mac.oranlar['X'] }}</div>
                </label>
                <label class="oran-btn">
                    <input type="radio" name="tahmin" value="MS 2">
                    <div class="oran-txt">2<br>{{ mac.oranlar['2'] }}</div>
                </label>
            </div>
            <div class="islem-alani">
                <input type="number" name="miktar" value="100" class="m-input">
                <button type="submit" class="submit-btn">BAHİS YAP</button>
            </div>
        </form>
    </div>
    {% endfor %}

    <div class="gecmis">
        <h4>📋 SON KUPONLARIM</h4>
        {% for k in kuponlar %}
        <div class="kupon">
            <b>{{ k.mac }}</b><br>
            Tahmin: {{ k.tahmin }} ({{ k.oran }}) | Miktar: {{ k.yatirilan }} TL
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
