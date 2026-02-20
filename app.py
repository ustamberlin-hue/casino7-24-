import http.client
import json
import os
import random
from flask import Flask, render_template, jsonify, request

# Flask uygulamasını başlatırken klasör yolunu netleştiriyoruz
app = Flask(__name__, template_folder='templates')
app.secret_key = 'casino724_fixed_pro'

# Anahtarların (Çift Key)
KEYS = [
    "cb458df450msh9375318d2ece064p125635jsn9da8cba2163c", 
    "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"
]

@app.route('/')
def index():
    # templates/index.html dosyasının varlığından emin olmalısın
    return render_template('index.html')

@app.route('/api/guncelle')
def api_guncelle():
    kaynak = request.args.get('kaynak', 'hititbet')
    
    # Her bir anahtarı sırayla dene (Failover)
    for key in KEYS:
        try:
            conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com", timeout=10)
            headers = {
                'x-rapidapi-key': key,
                'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
            }
            
            # Kaynağa göre veri miktarını ayarla (Hititbet için daha fazla maç)
            limit = "20" if kaynak == "hititbet" else "15"
            
            conn.request("GET", f"/v3/fixtures?next={limit}", headers=headers)
            res = conn.getresponse()
            
            # Limit aşımı kontrolü (429 Hatası)
            if res.status == 429:
                continue
                
            raw_data = res.read().decode("utf-8")
            data = json.loads(raw_data)
            
            if "response" in data and len(data["response"]) > 0:
                maclar = []
                for f in data["response"]:
                    maclar.append({
                        "lig": f['league']['name'],
                        "ev": f['teams']['home']['name'],
                        "dep": f['teams']['away']['name'],
                        # Gerçek oranlar API'de her lig için ücretsiz değildir, bu yüzden mantıklı random oran üretiyoruz
                        "o1": round(random.uniform(1.30, 3.80), 2),
                        "ox": round(random.uniform(3.05, 3.90), 2),
                        "o2": round(random.uniform(2.10, 5.50), 2)
                    })
                return jsonify({"status": "success", "maclar": maclar})
            
        except Exception as e:
            print(f"Hata oluştu ({key[:5]}...): {str(e)}")
            continue
        finally:
            conn.close()
            
    # Eğer tüm anahtarlar başarısız olursa
    return jsonify({
        "status": "error", 
        "message": "⚠️ Tüm veri kaynakları (Hititbet/Misli) şu an meşgul veya limit doldu."
    })

if __name__ == '__main__':
    # Render'ın port ayarını dinamik alması için
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
