from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Geçici veri tabanı (Gerçek bir projede SQL kullanılır)
player_data = {
    "username": "Hero_Developer",
    "level": 1,
    "hp": 100,
    "max_hp": 100,
    "stars": 0,
    "xp": 0
}

@app.route('/')
def index():
    # Bu rota, hazırladığımız HTML sayfasını kullanıcıya sunar
    return render_template('index.html')

@app.route('/battle/attack', methods=['POST'])
def attack():
    global player_data
    action = request.json.get('action')
    
    # Savaş Mantığı Arka Planda Dönüyor
    enemy_hp_loss = 0
    player_hp_loss = 0
    message = ""

    if action == "code_attack":
        enemy_hp_loss = random.randint(15, 25)
        message = f"Kod saldırısı başarılı! {enemy_hp_loss} hasar verildi."
    elif action == "merge_strike":
        enemy_hp_loss = random.randint(5, 40)
        message = f"Tehlikeli bir Merge! {enemy_hp_loss} hasar!"
    
    # Düşman da karşı saldırı yapar (Simülasyon)
    player_hp_loss = random.randint(8, 15)
    player_data["hp"] -= player_hp_loss

    # Sonuçları Frontend'e (HTML) geri gönder
    return jsonify({
        "message": message,
        "enemy_damage": enemy_hp_loss,
        "player_damage": player_hp_loss,
        "current_player_hp": player_data["hp"]
    })

import os

if __name__ == '__main__':
    # Render'ın verdiği portu al, yoksa 5000 kullan
    port = int(os.environ.get("PORT", 5000))
    # Host mutlaka 0.0.0.0 olmalı!
    app.run(host='0.0.0.0', port=port)
    
