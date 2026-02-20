import requests
from flask import Flask, render_template_string, request, session

app = Flask(__name__)
app.secret_key = 'sanal_iddaa_anahtari'

# API Ayarı (TheSportsDB ücretsiz test anahtarı)
API_URL = "https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php?id=4328"

def maclari_getir():
    try:
        r = requests.get(API_URL, timeout=5)
        return r.json().get('events', [])
    except:
        return []

@app.route('/')
def index():
    # Sanal bakiye ilk kez giriyorsa 1000 TL tanımla
    if 'bakiye' not in session:
        session['bakiye'] = 1000
    
    maclar = maclari_getir()
    return render_template_string(HTML_SABLONU, maclar=maclar, bakiye=session['bakiye'])

@app.route('/oyna', methods=['POST'])
def oyna():
    miktar = int(request.form.get('miktar', 0))
    if miktar > session['bakiye']:
        return "Yetersiz bakiye!", 400
    
    session['bakiye'] -= miktar
    return f"Bahis onaylandı! Kalan Bakiye: {session['bakiye']} TL"

HTML_SABLONU = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casino 7-24 Sanal</title>
    <style>
        body { background: #0b0d10; color: white; font-family: sans-serif; padding: 10px; }
        .kart { background: #1c1f26; border-radius: 10px; padding: 15px; margin-bottom: 10px; border-left: 4px solid #00ff41; }
        .bakiye { background: #00ff41; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
        input { width: 60px; padding: 5px; border-radius: 5px; border: none; }
        button { background: #00ff41; border: none; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="bakiye">SANAL CÜZDAN: {{ bakiye }} TL</div>
    <h3>⚽ Güncel Maçlar (Premier Lig)</h3>
    {% for mac in maclar %}
    <div class="kart">
        <div>{{ mac.strEvent }}</div>
        <small>{{ mac.dateEvent }}</small>
        <form action="/oyna" method="post" style="margin-top:10px;">
            <input type="number" name="miktar" value="10" min="1">
            <button type="submit">Bahis Yap</button>
        </form>
    </div>
    {% endfor %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
