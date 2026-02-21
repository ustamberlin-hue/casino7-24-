import streamlit as st

# Tam ekran için layout ayarı
st.set_page_config(page_title="Hızlı Şoför Pro", page_icon="🏎️", layout="wide")

# Kenar boşluklarını sıfırlayan CSS
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding: 0; }
    iframe { width: 100vw; height: 100vh; border: none; margin: 0; padding: 0; overflow: hidden; }
    body { margin: 0; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

oyun_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background: #222; font-family: Arial, sans-serif; }
        canvas { display: block; background: #444; touch-action: none; }
        #ui {
            position: absolute; top: 10px; left: 10px; color: white; 
            font-size: 20px; text-shadow: 2px 2px 4px #000; pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="ui">❤️ Can: <span id="lives">3</span> | 🏆 Skor: <span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const livesEl = document.getElementById("lives");
    const scoreEl = document.getElementById("score");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let lives = 3;
    let score = 0;
    let gameActive = true;
    let roadOffset = 0;

    // Arabayı düzelttik (Yatay değil dikey duracak)
    const player = { x: canvas.width / 2 - 25, y: canvas.height - 120, w: 50, h: 80 };
    let enemies = [];
    let powerups = [];

    // DOKUNMATİK KONTROL: Parmağın olduğu yere git
    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        let touch = e.touches[0];
        let targetX = touch.clientX - player.w / 2;
        // Sınırları koru
        if (targetX > 0 && targetX < canvas.width - player.w) {
            player.x = targetX;
        }
    }, { passive: false });

    function spawnEnemy() {
        if (Math.random() < 0.03) {
            enemies.push({ x: Math.random() * (canvas.width - 50), y: -100, w: 50, h: 80, speed: 5 + (score/15) });
        }
    }

    function spawnLife() {
        if (Math.random() < 0.005) {
            powerups.push({ x: Math.random() * (canvas.width - 40), y: -50, w: 40, h: 40, speed: 4 });
        }
    }

    function draw() {
        if (!gameActive) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Yol ve Çizgiler
        roadOffset += 7;
        ctx.strokeStyle = "rgba(255,255,255,0.5)";
        ctx.setLineDash([40, 40]);
        ctx.lineDashOffset = -roadOffset;
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0); ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();

        // OYUNCU (Araba düzeltildi: 🏎️ dik bakıyor)
        ctx.font = "60px Arial";
        ctx.save();
        ctx.translate(player.x + player.w/2, player.y + player.h/2);
        ctx.rotate(-Math.PI / 2); // Emojiyi dik konuma getirdik
        ctx.fillText("🏎️", -35, 25);
        ctx.restore();

        // DÜŞMANLAR (🚘)
        enemies.forEach((en, i) => {
            en.y += en.speed;
            ctx.save();
            ctx.translate(en.x + en.w/2, en.y + en.h/2);
            ctx.rotate(Math.PI / 2); // Karşıdan gelenler ters bakmalı
            ctx.fillText("🚘", -35, 25);
            ctx.restore();

            // Çarpışma
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

        // CANLAR (❤️)
        powerups.forEach((p, i) => {
            p.y += p.speed;
            ctx.fillText("❤️", p.x, p.y + 35);
            if (player.x < p.x + p.w && player.x + player.w > p.x && player.y < p.y + p.h && player.y + player.h > p.y) {
                powerups.splice(i, 1);
                lives++;
                livesEl.innerText = lives;
            }
            if (p.y > canvas.height) powerups.splice(i, 1);
        });

        spawnEnemy();
        spawnLife();
        requestAnimationFrame(draw);
    }
    draw();
</script>
</body>
</html>
"""

st.components.v1.html(oyun_html, height=2000) # Mobil ekranın tamamını kullanması için yüksek değer
