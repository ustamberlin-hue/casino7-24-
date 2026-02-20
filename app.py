import requests
import os
import random
from flask import Flask, render_template_string, session

app = Flask(__name__)
app.secret_key = 'casino_724_ultra_bulten'

def ultra_bulten_cek():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Zorlanmış Veri Havuzu (Tüm açık arşiv linkleri)
    linkler = [
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/11/90.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/43/3.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/2/44.json",
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/16/37.json"
    ]
    
    toplam_maclar = []
    lig_listesi = ["Trendyol Süper Lig", "İngiltere Premier Lig", "İspanya La Liga", "Almanya Bundesliga", "İtalya Serie A", "Fransa Ligue 1", "Şampiyonlar Ligi"]

    for url in linkler:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                for m in res.json():
                    toplam_maclar.append({
                        "lig": random.choice(lig_listesi),
                        "ev": m['home_team']['home_team_name'],
                        "dep": m['away_team']['away_team_name'],
                        "o1": round(random.uniform(1.20, 5.00), 2),
                        "ox": round(random.uniform(3.00, 4.50), 2),
                        "o2": round(random.uniform(1.80, 8.00), 2)
                    })
        except: continue
    
    # Listeyi karıştır ki her seferinde farklı maçlar üstte gelsin
    random.shuffle(toplam_maclar)
    return toplam_maclar

@app.route('/')
def index():
    if 'bakiye' not in session: session['bakiye'] = 1000
    maclar = ultra_bulten_cek()
    return render_template_string(ULTRA_TASARIM, maclar=maclar, bakiye=session['bakiye'])

# --- PROFESYONEL BÜLTEN TASARIMI ---
ULTRA_TASARIM = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CASINO 7-24 | ULTRA BÜLTEN</title>
    <style>
        body { background: #0b0e14; color: white; font-family: 'Inter', sans-serif; margin: 0; padding-bottom: 50px; }
        .ust-panel { background: #161b22; padding: 15px; border-bottom: 2px solid #00ff41; position: sticky; top: 0; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .lig-baslik { background: #21262d; padding: 8px 15px; font-size: 13px; color: #00ff41; font-weight: bold; margin-top: 10px; border-left: 4px solid #00ff41; }
        .mac-kart { background: #161b22; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .oran-sirasi { display: flex; gap: 5px; margin-top: 10px; }
        .oran-kutusu { flex: 1; background: #0d1117; border: 1px solid #30363d; padding: 8px; text-align: center; border-radius: 4px; }
        .bakiye-badge { background: #00ff41; color: black; padding: 4px 12px; border-radius: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="ust-panel">
        <span style="font-weight: 900; letter-spacing: 1px;">CASINO 7-24</span>
        <div class="bakiye-badge">💰 {{ bakiye }} TL</div>
    </div>

    <div style="padding: 10px; text-align: center; color: #8b949e; font-size: 12px;">
        GÜNCEL FUTBOL BÜLTENİ ({{ maclar|length }} MAÇ AKTİF)
    </div>

    {% for m in maclar %}
    <div class="lig-baslik">{{ m.lig }}</div>
    <div class="mac-kart">
        <div style="display: flex; justify-content: space-between; font-weight: 500;">
            <span>{{ m.ev }}</span>
            <span style="color: #8b949e;">-</span>
            <span>{{ m.dep }}</span>
        </div>
        <div class="oran-sirasi">
            <div class="oran-kutusu"><small style="color:#8b949e">1</small><br>{{ m.o1 }}</div>
            <div class="oran-kutusu"><small style="color:#8b949e">X</small><br>{{ m.ox }}</div>
            <div class="oran-kutusu"><small style="color:#8b949e">2</small><br>{{ m.o2 }}</div>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
