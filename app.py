import http.client
import json
import os
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino_724_weekly_bulten'

def haftalik_bulten_cek():
    API_KEY = "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # Önümüzdeki 7 günü kapsayan maçları çekiyoruz
        baslangic = datetime.now().strftime('%Y-%m-%d')
        bitis = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Önemli liglerin ID'leri (Süper Lig: 203, Premier Lig: 39, La Liga: 140)
        # Hepsini tek seferde çekmek için tarih aralığı kullanıyoruz
        conn.request("GET", f"/v3/fixtures?from={baslangic}&to={bitis}", headers=headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        bulten = []
        for f in data.get("response", []):
            # Maç tarihini güzelleştirme
            mac_tarihi = datetime.fromisoformat(f['fixture']['date']).strftime('%d.%m %H:%M')
            
            bulten.append({
                "tarih": mac_tarihi,
                "lig": f['league']['name'],
                "ulke": f['league']['country'],
                "ev": f['teams']['home']['name'],
                "dep": f['teams']['away']['name'],
                "durum": f['fixture']['status']['short'],
                "o1": round(random.uniform(1.40, 4.50), 2),
                "ox": round(random.uniform(3.10, 4.20), 2),
                "o2": round(random.uniform(2.10, 6.50), 2)
            })
        
        # Maçları tarihe göre sırala
        return sorted(bulten, key=lambda x: x['tarih'])
    except:
        return []

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = haftalik_bulten_cek()
    return render_template_string(HAFTALIK_TASARIM, maclar=maclar, bakiye=session['bakiye'])

# --- HAFTALIK BÜLTEN TASARIMI ---
HAFTALIK_TASARIM = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | HAFTALIK BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: 'Inter', sans-serif; margin: 0; padding-bottom: 50px; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; position: sticky; top: 0; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .lig-baslik { background: #21262d; padding: 5px 15px; font-size: 12px; color: #8b949e; border-top: 1px solid #30363d; display: flex; justify-content: space-between; }
        .mac-kart { background: #161b22; margin-bottom: 2px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
        .takimlar-satir { display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: 500; }
        .tarih-saat { color: #00ff41; font-size: 11px; font-weight: bold; }
        .oran-grubu { display: flex; gap: 5px; }
        .oran-btn { flex: 1; background: #0d1117; border: 1px solid #30363d; padding: 10px; text-align: center; border-radius: 6px; cursor: pointer; color: #58a6ff; }
        .oran-btn:hover { border-color: #00ff41; }
        .bakiye-badge { background: #00ff41; color: black; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <span style="font-weight: 900;">CASINO 7-24</span>
        <div class="bakiye-badge">💰 {{ bakiye }} TL</div>
    </div>

    <div style="padding: 15px; font-weight: bold; color: #00ff41; border-bottom: 1px solid #30363d;">
        📅 7 GÜNLÜK FUTBOL BÜLTENİ
    </div>

    {% for m in maclar %}
    <div class="lig-baslik">
        <span>{{ m.ulke }} - {{ m.lig }}</span>
        <span class="tarih-saat">{{ m.tarih }}</span>
    </div>
    <div class="mac-kart">
        <div class="takimlar-satir">
            <span style="flex:1;">{{ m.ev }}</span>
            <span style="color:#30363d; padding: 0 10px;">vs</span>
            <span style="flex:1; text-align:right;">{{ m.dep }}</span>
        </div>
        <div class="oran-grubu">
            <div class="oran-btn"><small style="color:#8b949e; display:block;">1</small><b>{{ m.o1 }}</b></div>
            <div class="oran-btn"><small style="color:#8b949e; display:block;">X</small><b>{{ m.ox }}</b></div>
            <div class="oran-btn"><small style="color:#8b949e; display:block;">2</small><b>{{ m.o2 }}</b></div>
        </div>
    </div>
    {% endfor %}

    {% if not maclar %}
    <div style="text-align:center; padding:100px; color:#8b949e;">Bülten yüklenirken bir sorun oluştu veya maç bulunamadı.</div>
    {% endif %}
</body>
</html>
