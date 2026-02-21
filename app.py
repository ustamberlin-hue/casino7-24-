import streamlit as st

st.set_page_config(page_title="Pro Şoför", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {margin: 0; padding: 0;}
    iframe {width: 100vw; height: 90vh; border: none;}
    </style>
    """, unsafe_allow_html=True)

oyun_html = """
<div id="game-wrapper" style="width: 100%; height: 100vh; background: #333; display: flex; flex-direction: column; align-items: center; overflow: hidden;">
    <div style="color: white; padding: 10px; font-family: sans-serif; display: flex; gap: 20px; font-size: 20px;">
        <span>🏆 Skor: <b id="score">0</b></span>
        <span>❤️ Can: <b id="lives">3</b></span>
    </div>
    <canvas id="road" style="background: #444; border-left: 5px solid white; border-right: 5px solid white; touch-action: none;"></canvas>
    
    <div style="position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: space-around;">
        <button id="leftBtn" style="width: 120px; height: 80px; font-size: 30px; border-radius: 50%; border: none; background: rgba(255,255,255,0.2); color: white;">⬅️</button>
        <button id="rightBtn" style="width: 120px; height: 80px; font-size: 30px; border-radius: 50%; border: none; background: rgba(255,255,255,0.2); color: white;">➡️</button>
    </div>
</div>

<script>
    const canvas = document.getElementById("road");
    const ctx = canvas.getContext("2d");
    const scoreEl = document.getElementById("score");
    const livesEl = document.getElementById("lives");

    // Ekran boyutuna göre ayarla
    canvas.width = window.innerWidth > 500 ? 400 : window.innerWidth - 40;
    canvas.height = window.innerHeight * 0.7;

    let score = 0;
    let lives = 3;
    let gameActive = true;
    let roadOffset = 0;

    // Görseller (Emoji kullanarak gerçekçi araç hissi)
    const playerImg = "🏎️";
    const enemyImg = "🚘";
    const lifeImg = "❤️";

    let player = { x: canvas.width / 2 - 25, y: canvas.height - 100, w: 50, h: 80 };
    let enemies = [];
    let powerups = [];

    function spawnEnemy() {
        if (gameActive && Math.random() < 0.02) {
            enemies.push({ x: Math.random() * (canvas.width - 50), y: -100, w: 50, h: 80, speed: 4 });
        }
    }

    function spawnPowerup() {
        if (gameActive && Math.random() < 0.005) {
            powerups.push({ x: Math.random() * (canvas.width - 30), y: -50, w: 30, h: 30, speed: 3 });
        }
    }

    function update() {
        if (!gameActive) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Yol Çizgileri
        roadOffset += 5;
        ctx.strokeStyle = "white";
        ctx.setLineDash([30, 30]);
        ctx.lineDashOffset = -roadOffset;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();

        // Oyuncu Çizimi
        ctx.font = "60px Arial";
        ctx.fillText(playerImg, player.x, player.y + 60);

        // Düşman Arabalar
        enemies.forEach((en, i) => {
            ctx.fillText(enemyImg, en.x, en.y + 60);
            en.y += en.speed;

            // Çarpışma (Can Azalma)
            if (player.x < en.x + en.w && player.x + player.w > en.x && player.y < en.y + en.h && player.y + player.h > en.y) {
                enemies.splice(i, 1);
                lives--;
                livesEl.innerText = lives;
                if (lives <= 0) {
                    gameActive = false;
                    alert("OYUN BİTTİ! Skor: " + score);
                    location.reload();
                }
            }
            if (en.y > canvas.height) { enemies.splice(i, 1); score++; scoreEl.innerText = score; }
        });

        // Can Toplama
        powerups.forEach((p, i) => {
            ctx.font = "30px Arial";
            ctx.fillText(lifeImg, p.x, p.y + 30);
            p.y += p.speed;
            if (player.x < p.x + p.w && player.x + player.w > p.x && player.y < p.y + p.h && player.y + player.h > p.y) {
                powerups.splice(i, 1);
                lives++;
                livesEl.innerText = lives;
            }
        });

        spawnEnemy();
        spawnPowerup();
        requestAnimationFrame(update);
    }

    // Kontroller
    document.getElementById("leftBtn").onclick = () => { if (player.x > 10) player.x -= 40; };
    document.getElementById("rightBtn").onclick = () => { if (player.x < canvas.width - 60) player.x += 40; };
    
    update();
</script>
"""

st.components.v1.html(oyun_html, height=800)
