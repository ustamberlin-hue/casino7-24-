import requests
import os
import random
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'casino_kesin_cozum_724'

def gercek_mac_verisi():
    # Engellere takılmayan, GitHub üzerindeki ücretsiz ve gerçek maç arşivi
    url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/11/90.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Buradan gerçek takımları (Barcelona, Real Madrid vb.) çekiyoruz
            return [{
                "ev": m['home_team']['home_team_name'],
                "dep": m['away_team']['away_team_name'],
                "lig": "Uluslararası Lig",
                "o1": round(random.uniform(1.40, 3.50), 2),
                "ox": round(random.uniform(3.00, 4.00), 2),
                "o2": round(random.uniform(2.10, 5.50), 2)
            } for m in data[:12]]
    except:
        return []
    return []

@app.route('/')
def index():
    maclar = gercek_mac_verisi()
    return render_template_string(TASARIM, maclar=maclar)

TASARIM = """
<body style="background:#0b0e14; color:white; font-family:sans-serif; text-align:center; padding:20px;">
    <h1 style="color:#00ff41;">CASINO 7-24</h1>
    <p>💰 Bakiye: 1000 TL</p>
    {% for m in maclar %}
    <div style="background:#161b22; margin:10px auto; padding:15px; border-radius:10px; border:1px solid #333; max-width:400px;">
        <small style="color:#00ff41;">{{ m.lig }}</small><br>
        <b>{{ m.ev }} vs {{ m.dep }}</b><br>
        <div style="margin-top:10px;">
            <button style="background:#21262d; color:white; border:1px solid #444; padding:5px 15px;">1: {{ m.o1 }}</button>
            <button style="background:#21262d; color:white; border:1px solid #444; padding:5px 15px;">X: {{ m.ox }}</button>
            <button style="background:#21262d; color:white; border:1px solid #444; padding:5px 15px;">2: {{ m.o2 }}</button>
        </div>
    </div>
    {% endfor %}
</body>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
