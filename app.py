import http.client
import json
import os
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino_724_haftalik_dev_bulten'

def haftalik_bulten_cek():
    # Senin RapidAPI Anahtarın
    API_KEY = "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Bugün ve 7 gün sonrası arasındaki tüm maçlar
        bugun = datetime.now().strftime('%Y-%m-%d')
        gelecek = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Sadece popüler ligleri çekerek bülteni dolduruyoruz
        # Premier Lig (39), Süper Lig (203), La Liga (140) vb.
        conn.request("GET", f"/v3/fixtures?from={bugun}&to={gelecek}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        bulten = []
        for f in data.get("response", []):
            tarih_ham = datetime.fromisoformat(f['fixture']['date'].replace('Z', '+00:00'))
            bulten.append({
                "tarih": tarih_ham.strftime('%d.%m %H:%M'),
                "lig": f['league']['name'],
                "ev": f['teams']['home']['name'],
                "dep": f['teams']['away']['name'],
                "o1": round(random.uniform(1.40, 4.80), 2),
                "ox": round(random.uniform(3.10, 4.10), 2),
                "o2": round(random.uniform(2.10, 7.50), 2)
            })
        return bulten
    except:
        return []

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = haftalik_bulten_cek()
    return render_template_string(ULTRA_TASARIM, maclar=maclar, bakiye=session['bakiye'])

# --- SENİN SEVDİĞİN TASARIM ---
ULTRA_TASARIM = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | DEV BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: sans-serif; margin: 0; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; position: sticky; top: 0; display: flex; justify-content: space-between; align-items: center; z-index: 100; }
        .lig-baslik { background: #21262d; padding: 8px 15px; font-size: 13px; color: #00ff41; font-weight: bold; margin-top: 10px; border-left: 4px solid #00ff41; }
        .mac-kart { background: #161b22; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .oran-sirasi { display: flex; gap: 5px; margin-top: 10px; }
        .oran-kutusu { flex: 1; background: #0d1117; border: 1px solid #30363d; padding: 8px; text-align: center; border-radius: 4px; color: #00ff41; }
        .bakiye-badge { background: #00ff41; color: black; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <span style="font-weight: 900;">CASINO 7-24</span>
        <div class="bakiye-badge">💰 {{ bakiye }} TL</div>
    </div>

    <div style="padding: 10px; text-align: center; color: #8b949e; font-size: 12px;">📅 HAFTALIK GÜNCEL BÜLTEN</div>

    {% for m in maclar %}
    <div class="lig-baslik">{{ m.lig }} <span style="float:right; color:#8b949e;">{{ m.tarih }}</span></div>
    <div class="mac-kart">
        <div style="display: flex; justify-content: space-between; font-weight: 500;">
            <span>{{ m.ev }}</span>
            <span style="color: #8b949e;">vs</span>
            <span>{{ m.dep }}</span>
        </div>
        <div class="oran-sirasi">
            <div class="oran-kutusu"><small style="color:#888">1</small><br>{{ m.o1 }}</div>
            <div class="oran-kutusu"><small style="color:#888">X</small><br>{{ m.ox }}</div>
            <div class="oran-kutusu"><small style="color:#888">2</small><br>{{ m.o2 }}</div>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
