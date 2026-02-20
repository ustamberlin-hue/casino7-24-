import http.client
import json
import os
import random
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino_724_real_live_final'

def gercek_canli_verileri_cek():
    # Senin verdiğin RapidAPI Key
    API_KEY = "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
    
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # ŞU AN OYNANAN TÜM GERÇEK CANLI MAÇLAR
        conn.request("GET", "/v3/fixtures?live=all", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        canli_bulten = []
        for f in data.get("response", []):
            canli_bulten.append({
                "lig": f['league']['name'],
                "ev": f['teams']['home']['name'],
                "dep": f['teams']['away']['name'],
                "skor": f"{f['goals']['home']} - {f['goals']['away']}",
                "dakika": f['fixture']['status']['elapsed'],
                # API Oranları (Gerçekçi simülasyon)
                "o1": round(random.uniform(1.40, 4.50), 2),
                "ox": round(random.uniform(3.10, 4.00), 2),
                "o2": round(random.uniform(2.10, 6.00), 2)
            })
        return canli_bulten
    except:
        return []

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = gercek_canli_verileri_cek()
    return render_template_string(ULTRA_TASARIM, maclar=maclar, bakiye=session['bakiye'])

# --- SENİN TASARIMIN (CANLI VERİYLE GÜNCELLENDİ) ---
ULTRA_TASARIM = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | CANLI BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: 'Inter', sans-serif; margin: 0; padding-bottom: 50px; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; position: sticky; top: 0; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .live-badge { background: #ff004c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; animation: blinker 1.5s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
        .lig-baslik { background: #21262d; padding: 8px 15px; font-size: 13px; color: #00ff41; font-weight: bold; margin-top: 10px; border-left: 4px solid #00ff41; }
        .mac-kart { background: #161b22; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .skor-kutusu { background: #0d1117; padding: 5px 15px; border-radius: 5px; color: #00ff41; font-weight: bold; font-size: 18px; }
        .oran-sirasi { display: flex; gap: 5px; margin-top: 10px; }
        .oran-kutusu { flex: 1; background: #0d1117; border: 1px solid #30363d; padding: 8px; text-align: center; border-radius: 4px; cursor: pointer; }
        .bakiye-badge { background: #00ff41; color: black; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <span style="font-weight: 900; letter-spacing: 1px;">CASINO 7-24</span>
        <div class="bakiye-badge">💰 {{ bakiye }} TL</div>
    </div>

    <div style="padding: 10px; text-align: center; color: #8b949e; font-size: 12px;">
        🔴 CANLI GERÇEK MAÇLAR ({{ maclar|length }} MAÇ ŞU AN OYNANIYOR)
    </div>

    {% for m in maclar %}
    <div class="lig-baslik">{{ m.lig }} <span class="live-badge">{{ m.dakika }}'</span></div>
    <div class="mac-kart">
        <div style="display: flex; justify-content: space-between; align-items: center; font-weight: 500;">
            <span style="flex:1; text-align:right; padding-right:10px;">{{ m.ev }}</span>
            <span class="skor-kutusu">{{ m.skor }}</span>
            <span style="flex:1; text-align:left; padding-left:10px;">{{ m.dep }}</span>
        </div>
        <div class="oran-sirasi">
            <div class="oran-kutusu"><small style="color:#8b949e">1</small><br>{{ m.o1 }}</div>
            <div class="oran-kutusu"><small style="color:#8b949e">X</small><br>{{ m.ox }}</div>
            <div class="oran-kutusu"><small style="color:#8b949e">2</small><br>{{ m.o2 }}</div>
        </div>
    </div>
    {% endfor %}
    
    {% if not maclar %}
    <div style="text-align:center; padding:50px; color:#8b949e;">Şu an canlı maç bulunamadı.</div>
    {% endif %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
