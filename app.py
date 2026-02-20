import http.client
import json
import os
import random
import time
from datetime import datetime
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino724_smart_cache'

# HAFIZA SİSTEMİ (Caching)
cache = {
    "maclar": [],
    "son_guncelleme": 0
}

def akilli_bulten_cek():
    su_an = time.time()
    # Eğer son 30 dakika içinde veri çekildiyse, hafızadaki veriyi ver (Limiti korur)
    if cache["maclar"] and (su_an - cache["son_guncelleme"] < 1800):
        return cache["maclar"]

    API_KEY = "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Gerçekten oynanacak sıradaki 50 maçı çekiyoruz
        conn.request("GET", "/v3/fixtures?next=50", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        yeni_maclar = []
        if "response" in data:
            for f in data["response"]:
                tarih_ham = f['fixture']['date']
                tarih_format = datetime.fromisoformat(tarih_ham.replace('Z', '+00:00')).strftime('%d.%m %H:%M')
                
                yeni_maclar.append({
                    "tarih": tarih_format,
                    "lig": f['league']['name'],
                    "ev": f['teams']['home']['name'],
                    "dep": f['teams']['away']['name'],
                    "o1": round(random.uniform(1.45, 4.20), 2),
                    "ox": round(random.uniform(3.15, 3.85), 2),
                    "o2": round(random.uniform(2.15, 5.50), 2)
                })
            
            # Veri başarıyla geldiyse hafızaya kaydet
            cache["maclar"] = yeni_maclar
            cache["son_guncelleme"] = su_an
            return yeni_maclar
    except Exception as e:
        print(f"API Hatası: {e}")
    
    return cache["maclar"] # Hata olsa bile eskiden kalanları göster

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = akilli_bulten_cek()
    return render_template_string(SMART_DESIGN, maclar=maclar, bakiye=session['bakiye'])

SMART_DESIGN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | AKILLI BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: sans-serif; margin: 0; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; display: flex; justify-content: space-between; }
        .mac-kart { background: #161b22; margin: 10px; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .oran-btn { background: #0d1117; border: 1px solid #444; color: #00ff41; padding: 10px; flex: 1; text-align: center; border-radius: 4px; font-weight: bold; }
        .saat { color: #8b949e; font-size: 11px; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <b style="letter-spacing:1px;">CASINO 7-24</b>
        <span style="background:#00ff41; color:black; padding:2px 10px; border-radius:10px; font-weight:bold;">💰 {{ bakiye }} TL</span>
    </div>
    
    <p style="text-align:center; color:#00ff41; font-size:11px; margin-top:15px;">📡 GERÇEK ZAMANLI VERİ AKIŞI AKTİF</p>

    {% if not maclar %}
    <div style="text-align:center; padding:100px; color:#ff4c4c;">
        <b>Bülten Bekleniyor...</b><br>
        <small>API limitin dolmuş olabilir, 1 saat sonra tekrar dene.</small>
    </div>
    {% endif %}

    {% for m in maclar %}
    <div class="mac-kart">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span class="saat">{{ m.lig }}</span>
            <span class="saat">{{ m.tarih }}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:15px; margin-bottom:15px;">
            <span style="flex:1;">{{ m.ev }}</span>
            <span style="color:#444; padding:0 10px;">-</span>
            <span style="flex:1; text-align:right;">{{ m.dep }}</span>
        </div>
        <div style="display:flex; gap:8px;">
            <div class="oran-btn">1<br>{{ m.o1 }}</div>
            <div class="oran-btn">X<br>{{ m.ox }}</div>
            <div class="oran-btn">2<br>{{ m.o2 }}</div>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
