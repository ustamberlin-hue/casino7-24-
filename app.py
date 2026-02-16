from flask import Flask, render_template, render_template_string, request, jsonify
import random
import time

app = Flask(__name__)

# --- SİSTEM VERİLERİ ---
# Maçlar sayfa her yenilendiğinde dakikaları ilerlemiş şekilde görünür
matches = [
    {"id": 1, "league": "Süper Lig", "home": "Galatasaray", "away": "Fenerbahçe", "score": [0, 0], "minute": 22, "odds": [1.85, 3.20, 2.10]},
    {"id": 2, "league": "Premier Lig", "home": "Man. City", "away": "Arsenal", "score": [1, 0], "minute": 44, "odds": [1.50, 3.80, 4.50]},
    {"id": 3, "league": "Şampiyonlar Ligi", "home": "Real Madrid", "away": "Bayern Münih", "score": [2, 2], "minute": 78, "odds": [2.40, 2.90, 2.30]},
    {"id": 4, "league": "Süper Lig", "home": "Beşiktaş", "away": "Trabzonspor", "score": [0, 1], "minute": 15, "odds": [2.10, 3.10, 2.80]}
]

# --- HTML / CSS (TEK DOSYA) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GokayBett Holding V2</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f0f0f; color: #e5e5e5; font-family: 'Inter', sans-serif; }
        .gold-text { color: #d4af37; }
        .gold-bg { background-color: #d4af37; }
        .card { background-color: #1a1a1a; border: 1px solid #333; }
        .btn-gold { background: linear-gradient(180deg, #d4af37 0%, #b8860b 100%); color: #000; font-weight: bold; }
        .live-dot { height: 8px; width: 8px; background-color: #ff4d4d; border-radius: 50%; display: inline-block; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <header class="p-4 border-b border-gray-800 flex justify-between items-center bg-black">
        <h1 class="text-2xl font-black gold-text italic">GOKAYBETT <span class="text-white">HOLDİNG</span></h1>
        <div class="text-xs text-right">
            <p class="text-gray-400">Üye Girişi</p>
            <p class="font-bold">Bakiye: 1.250,00 ₺</p>
        </div>
    </header>

    <main class="p-4 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2">
            <div class="flex gap-4 mb-4 overflow-x-auto pb-2">
                <button class="gold-bg text-black px-4 py-1 rounded text-sm font-bold">Canlı Bahis</button>
                <button class="bg-gray-800 px-4 py-1 rounded text-sm">Süper Lig</button>
                <button class="bg-gray-800 px-4 py-1 rounded text-sm">Basketbol</button>
                <button class="bg-gray-800 px-4 py-1 rounded text-sm text-yellow-500">VIP Analiz</button>
            </div>

            <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
                <span class="live-dot"></span> CANLI MÜSABAKALAR
            </h2>

            <div class="space-y-3">
                {% for match in matches %}
                <div class="card p-4 rounded-xl flex items-center justify-between">
                    <div class="flex-1">
                        <p class="text-[10px] text-gray-500 uppercase">{{ match.league }} • DK {{ match.minute }}'</p>
                        <div class="flex justify-between items-center pr-10">
                            <span class="font-semibold text-sm">{{ match.home }}</span>
                            <span class="gold-text font-bold">{{ match.score[0] }} - {{ match.score[1] }}</span>
                            <span class="font-semibold text-sm">{{ match.away }}</span>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="addToSlip('{{match.home}}', 'MS 1', {{match.odds[0]}})" class="bg-gray-900 border border-gray-700 hover:border-yellow-600 p-2 rounded w-14 text-center">
                            <p class="text-[10px] text-gray-500">1</p>
                            <p class="text-xs font-bold">{{ match.odds[0] }}</p>
                        </button>
                        <button onclick="addToSlip('X', 'Berabere', {{match.odds[1]}})" class="bg-gray-900 border border-gray-700 hover:border-yellow-600 p-2 rounded w-14 text-center">
                            <p class="text-[10px] text-gray-500">X</p>
                            <p class="text-xs font-bold">{{ match.odds[1] }}</p>
                        </button>
                        <button onclick="addToSlip('{{match.away}}', 'MS 2', {{match.odds[2]}})" class="bg-gray-900 border border-gray-700 hover:border-yellow-600 p-2 rounded w-14 text-center">
                            <p class="text-[10px] text-gray-500">2</p>
                            <p class="text-xs font-bold">{{ match.odds[2] }}</p>
                        </button>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="mt-10 card p-6 rounded-2xl bg-gradient-to-br from-[#1a1a1a] to-[#000]">
                <h3 class="gold-text font-bold mb-2">VIP ÜYELİK BAŞVURUSU</h3>
                <p class="text-xs text-gray-400 mb-4">Özel analizler ve yüksek limitli kuponlar için başvurun.</p>
                <div class="grid grid-cols-2 gap-4">
                    <input type="text" placeholder="Ad Soyad" class="bg-black border border-gray-800 p-2 rounded text-sm outline-none focus:border-yellow-600">
                    <input type="text" id="refCode" placeholder="Referans Kodu" class="bg-black border border-gray-800 p-2 rounded text-sm outline-none focus:border-yellow-600">
                </div>
                <button onclick="alert('Başvurunuz Alındı!')" class="w-full btn-gold mt-4 py-3 rounded-lg text-sm">HEMEN BAŞVUR</button>
            </div>
        </div>

        <div class="space-y-6">
            <div class="card p-5 rounded-2xl sticky top-4">
                <h3 class="text-center font-bold border-b border-gray-800 pb-3 mb-4">KUPONUM</h3>
                <div id="coupon-items" class="space-y-4 mb-6 min-h-[100px] text-sm italic text-gray-500 text-center">
                    Henüz maç seçilmedi.
                </div>
                <div class="border-t border-gray-800 pt-4 space-y-2">
                    <div class="flex justify-between text-sm">
                        <span>Toplam Oran:</span>
                        <span id="total-odds" class="gold-text font-bold">0.00</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>Miktar:</span>
                        <input type="number" value="100" class="bg-black border border-gray-700 w-20 text-right px-1 rounded">
                    </div>
                    <button onclick="alert('Kupon Başarıyla Onaylandı!')" class="w-full btn-gold py-4 rounded-xl mt-4">KUPONU ONAYLA</button>
                </div>
            </div>

            <div class="card p-4 rounded-xl">
                <h4 class="text-xs font-bold mb-2">BİTEN MAÇLAR</h4>
                <div class="text-[11px] space-y-2 text-gray-400">
                    <div class="flex justify-between border-b border-gray-800 pb-1"><span>Liverpool - Chelsea</span> <span class="text-green-500">2-1 (Bitti)</span></div>
                    <div class="flex justify-between border-b border-gray-800 pb-1"><span>Milan - Inter</span> <span class="text-green-500">0-0 (Bitti)</span></div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let slip = [];
        function addToSlip(team, type, odds) {
            const items = document.getElementById('coupon-items');
            if(slip.length == 0) items.innerHTML = '';
            
            slip.push(odds);
            let total = slip.reduce((a, b) => a * b, 1).toFixed(2);
            document.getElementById('total-odds').innerText = total;

            const div = document.createElement('div');
            div.className = 'bg-black p-2 rounded text-left border-l-2 border-yellow-600';
            div.innerHTML = `<p class="font-bold text-white text-xs">${team}</p><p class="text-[10px]">${type} | Oran: ${odds}</p>`;
            items.appendChild(div);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Simülasyon: Maç dakikalarını her girişte biraz ilerlet
    for m in matches:
        m['minute'] += random.randint(0, 2)
        if m['minute'] > 90: m['minute'] = 90
        # Rastgele gol ihtimali
        if random.random() > 0.95 and m['minute'] < 90:
            m['score'][random.randint(0, 1)] += 1
            
    return render_template_string(HTML_TEMPLATE, matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
