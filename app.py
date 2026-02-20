from flask import Flask, render_template, jsonify, request
import http.client, json, random

app = Flask(__name__)

# Çift Key Sistemi Aktif
KEYS = ["cb458df450msh9375318d2ece064p125635jsn9da8cba2163c", "2b59377c0emsh58c8daff7d6d736p141086jsnb172a65d9ee9"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/guncelle')
def api_guncelle():
    kaynak = request.args.get('kaynak', 'hititbet')
    
    # Gerçek API Sorgusu
    for key in KEYS:
        try:
            conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
            headers = {'x-rapidapi-key': key, 'x-rapidapi-host': "api-football-v1.p.rapidapi.com"}
            # Kaynağa göre farklı sayıda maç çekerek çeşitlilik sağlıyoruz
            limit = "15" if kaynak == "hititbet" else "25"
            conn.request("GET", f"/v3/fixtures?next={limit}", headers=headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            
            if "response" in data:
                maclar = []
                for f in data["response"]:
                    maclar.append({
                        "lig": f['league']['name'],
                        "ev": f['teams']['home']['name'],
                        "dep": f['teams']['away']['name'],
                        "o1": round(random.uniform(1.3, 3.5), 2),
                        "ox": round(random.uniform(3.1, 4.0), 2),
                        "o2": round(random.uniform(2.1, 5.0), 2)
                    })
                return jsonify({"status": "success", "maclar": maclar})
        except: continue
        
    return jsonify({"status": "error", "message": "Kaynaklara şu an bağlanılamıyor. Limit dolmuş olabilir."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
