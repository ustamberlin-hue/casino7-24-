import streamlit as st

st.set_page_config(page_title="Hızlı Şoför Pro", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    /* Ekranın kaymasını ve taşmasını engelle */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden;
        height: 100vh;
        margin: 0;
        padding: 0;
    }
    iframe {
        width: 100vw;
        height: 100vh;
        border: none;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

oyun_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background: #222; }
        canvas { display: block; background: #444; margin: 0 auto; }
        #ui {
            position: absolute; top: 10px; width: 100%; text-align: center;
            color: white; font-size: 18px; font-family: sans-serif; z-index: 10;
        }
    </style>
</head>
<body>
    <div id="ui">❤️ <span id="lives">3</span> | 🏆 <span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const livesEl = document.getElementById("lives");
    const scoreEl = document.getElementById("score");

    // Ekranı tam sığdır
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let lives = 3;
    let score = 0;
    let gameActive = true;
    let roadOffset = 0;

    // ARACIN KONUMU: Görünmesi için yukarı çekildi
    const player = { x: canvas.width / 2 - 25, y: canvas.height - 180, w: 50, h: 80 };
    let enemies = [];
    let powerups = [];

    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        let touch = e.touches[0];
        player.x = touch.clientX - player.w / 2;
    }, { passive: false });

    function spawnEnemy() {
        if (Math.random() < 0.03) {
            enemies.push({ x: Math.random() * (canvas.width - 50), y: -100, w: 50, h: 80, speed: 5 });
        }
    }

    function draw() {
        if (!gameActive) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Yol Çizgileri
        roadOffset += 7;
        ctx.strokeStyle = "white";
        ctx.setLineDash([40, 40]);
        ctx.lineDashOffset = -roadOffset;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0); ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();

        // Kendi Aracın (Dik Konumda)
        ctx.font = "60px Arial";
        ctx.save();
        ctx.translate(player.x + player.w/2, player.y + player.h/2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText("🏎️", -35, 25);
        ctx.restore();

        // Diğer Arabalar
        enemies.forEach((en, i) => {
            en.y += en.speed;
            ctx.save();
            ctx.translate(en.x + en.w/2, en.y + en.h/2);
            ctx.rotate(Math.PI / 2);
            ctx.fillText("🚘", -35, 25);
            ctx.restore();

            if (player.x < en.x + en.w && player.x + player.w > en.x && player.y < en.y + en.h && player.y + player.h > en.y) {
                enemies.splice(i, 1);
                lives--;
                livesEl.innerText = lives;
                if(lives <= 0) { gameActive = false; alert("BİTTİ! Skor: " + score); location.reload(); }
            }
            if (en.y > canvas.height) { enemies.splice(i, 1); score++; scoreEl.innerText = score; }
        });

        spawnEnemy();
        requestAnimationFrame(draw);
    }
    draw();
</script>
</body>
</html>
