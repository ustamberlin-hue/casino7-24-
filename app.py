import http.client
import json
import os
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino_724_fixed_v3'

def haftalik_bulten_cek():
    API_KEY = "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    
    try:
        # API'yi yormamak için sadece bugün ve yarının maçlarını istiyoruz
        bugun = datetime.now().strftime('%Y-%m-%d')
        # ÖNEMLİ: Daha fazla maç için sadece 'next=50' (Sıradaki 50 maç) parametresini kullanıyoruz
        conn.request("GET", "/v3/fixtures?next=50", headers=headers)
        
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        bulten = []
        # Eğer API'den veri gelirse işle
        if "response" in data and len(data["response"]) > 0:
            for f in data["response"]:
                tarih_ham = f['fixture']['date']
                tarih_format = datetime.fromisoformat(tarih_ham.replace('Z', '+00:00')).strftime('%d.%m %H:%M')
                
                bulten.append({
                    "tarih": tarih_format,
                    "lig": f['league']['name'],
                    "ev": f['teams']['home']['name'],
                    "dep": f['teams']['away']['name'],
                    "o1": round(random.uniform(1.35, 4.50), 2),
                    "ox": round(random.uniform(3.10, 3.90), 2),
                    "o2": round(random.uniform(1.90, 6.00), 2)
                })
        return bulten
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = haftalik_bulten_cek()
    return render_template_string(ULTRA_TASARIM, maclar=maclar, bakiye=session['bakiye'])

# Tasarımı biraz daha sağlamlaştırdım (Maç yoksa uyarı verir)
ULTRA_TASARIM = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | HAFTALIK BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: sans-serif; margin: 0; padding-bottom: 30px; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; position: sticky; top: 0; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .lig-baslik { background: #21262d; padding: 8px 15px; font-size: 13px; color: #00ff41; font-weight: bold; margin-top: 10px; border-left: 4px solid #00ff41; }
        .mac-kart { background: #161b22; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .oran-sirasi { display: flex; gap: 5px; margin-top: 10px; }
        .oran-kutusu { flex: 1; background: #0d1117; border: 1px solid #30363d; padding: 10px; text-align: center; border-radius: 4px; color: #00ff41; font-weight: bold; }
        .bakiye-badge { background: #00ff41; color: black; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <span style="font-weight: 900;">CASINO 7-24</span>
        <div class="bakiye-badge">💰 {{ bakiye }} TL</div>
    </div>

    <div style="padding: 10px; text-align: center; color: #8b949e; font-size: 13px;">📅 GÜNCEL HAFTALIK BÜLTEN ({{ maclar|length }} Maç)</div>

    {% for m in maclar %}
    <div class="lig-baslik">{{ m.lig }} <span style="float:right; color:#8b949e; font-size:11px;">{{ m.tarih }}</span></div>
    <div class="mac-kart">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="flex:1;">{{ m.ev }}</span>
            <span style="color: #444; padding: 0 10px;">vs</span>
            <span style="flex:1; text-align:right;">{{ m.dep }}</span>
        </div>
        <div class="oran-sirasi">
            <div class="oran-kutusu">1<br>{{ m.o1 }}</div>
            <div class="oran-kutusu">X<br>{{ m.ox }}</div>
            <div class="oran-kutusu">2<br>{{ m.o2 }}</div>
        </div>
    </div>
    {% endfor %}

    {% if not maclar %}
    <div style="text-align:center; padding:100px; color:#ff4c4c;">
        ⚠️ Bülten yüklenemedi!<br>
        <small style="color:#888;">API anahtarını kontrol et veya biraz bekle.</small>
    </div>
    {% endif %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
