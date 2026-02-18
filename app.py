from flask import Flask, render_template_string, jsonify, request
import os
import random

app = Flask(__name__)

# OYUNUN GÖRSELİ (HTML BURADA)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>The Commit Theory - CANLI</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .box { border: 2px solid #58a6ff; padding: 20px; display: inline-block; border-radius: 10px; background: #161b22; }
        h1 { color: #58a6ff; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🚀 OYUN BAŞLADI!</h1>
        <p>GitHub Savaşçısı Hoş Geldin.</p>
        <div id="stats">Level: 1 | HP: 100</div>
        <br>
        <button onclick="alert('Kod Saldırısı Yapıldı!')">SALDIRI YAP</button>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Templates klasörüne gerek kalmadan direkt HTML'i basar
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Render için gerekli port ayarları
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
