import http.client
import json
import os
import random
import time
from datetime import datetime
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino724_dual_key_system'

# VERİ KAYIT DOSYASI (Hafıza Dosyası)
DATA_FILE = "bulten_cache.json"

def bulten_kaydet(veri):
    with open(DATA_FILE, 'w') as f:
        json.dump({"zaman": time.time(), "maclar": veri}, f)

def bulten_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data["maclar"], data["zaman"]
        except: return [], 0
    return [], 0

def gercek_bulten_getir():
    mevcut_maclar, son_zaman = bulten_yukle()
    su_an = time.time()

    # 15 DAKİKADA BİR GÜNCELLE (Limiti korumak için ideal süre)
    if mevcut_maclar and (su_an - son_zaman < 900):
        return mevcut_maclar

    # ANAHTAR LİSTESİ (Biri biterse diğeri devreye girer)
    ANAHTARLAR = [
        "cb458df450msh9375318d2ece064p125635jsn9da8cba2163c", # Yeni taze anahtarın
        "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"  # Eski anahtarın
    ]
    
    for KEY in ANAHTARLAR:
        try:
            conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': KEY,
                'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
            }
            conn.request("GET", "/v3/fixtures?next=40", headers=headers)
            res = conn.getresponse()
            
            if res.status == 429: # Limit dolduysa sonraki key'e geç
                continue
                
            raw_data = json.loads(res.read().decode("utf-8"))
            
            yeni_list = []
            if "response" in raw_data and len(raw_data["response"]) > 0:
                for f in raw_data["response"]:
                    t_iso = f['fixture']['date']
                    t_str = datetime.fromisoformat(t_iso.replace('Z', '+00:00')).strftime('%d.%m %H:%M')
                    
                    yeni_list.append({
                        "lig": f['league']['name'],
                        "ev": f['teams']['home']['name'],
                        "dep": f['teams']['away']['name'],
                        "tarih": t_str,
                        "o1": round(random.uniform(1.40, 4.50), 2),
                        "ox": round(random.uniform(3.10, 3.80), 2),
                        "o2": round(random.uniform(2.10, 6.00), 2)
                    })
                bulten_kaydet(yeni_list)
                return yeni_list
        except:
            continue
    
    return mevcut_maclar # Hiçbiri çalışmazsa hafızadakini göster

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = gercek_bulten_getir()
    return render_template_string(PRO_DESIGN, maclar=maclar, bakiye=session['bakiye'])

# Tasarım aynı kalıyor... (PRO_DESIGN kodunu yukarıdaki gibi kullanabilirsin)
PRO_DESIGN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | GERÇEK VERİ</title>
    <style>
        body { background: #0b0e14; color: white; font-family: sans-serif; margin: 0; }
        .header { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; display: flex; justify-content: space-between; }
        .mac-kart { background: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin: 10px; }
        .odd-box { flex: 1; background: #0d1117; border: 1px solid #444; padding: 10px; text-align: center; border-radius: 6px; color: #00ff41; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <span style="font-weight: 900; color: #00ff41;">CASINO 7-24</span>
        <div style="background: #238636; color: white; padding: 5px 15px; border-radius: 20px;">💰 {{ bakiye }} TL</div>
    </div>
    <div style="padding: 10px;">
        {% for m in maclar %}
        <div class="mac-kart">
            <div style="font-size:11px; color:#8b949e; margin-bottom:5px;">{{ m.lig }} • {{ m.tarih }}</div>
            <div style="display:flex; justify-content:space-between; font-weight:bold; margin-bottom:10px;">
                <span>{{ m.ev }}</span> <span style="color:#00ff41;">VS</span> <span>{{ m.dep }}</span>
            </div>
            <div style="display:flex; gap:8px;">
                <div class="odd-box">1<br>{{ m.o1 }}</div>
                <div class="odd-box">X<br>{{ m.ox }}</div>
                <div class="odd-box">2<br>{{ m.o2 }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
