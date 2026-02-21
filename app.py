import streamlit as st

st.set_page_config(page_title="Pro Simülasyon", layout="wide")

# Ekranı temizleyen CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { overflow: hidden; height: 100vh; background: #222; }
    iframe { width: 100vw; height: 100vh; border: none; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# Hata vermemesi için tırnaklara dikkat ederek HTML kodunu ekliyoruz
oyun_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background: #333; font-family: sans-serif; }
        canvas { display: block; touch-action: none; background: #444; }
        #hud {
            position: absolute; top: 10px; width: 100%; display: flex;
            justify-content: space-around; color: white; font-size: 20px;
            text-shadow: 2px 2px 4px #000; pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="hud">
        <span>❤️ Can: <b id="lives">3</b></span>
        <span>🏆 Skor: <b id="score">0</b></span>
    </div>
    <canvas id="game"></canvas>

<script>
    const canvas = document.getElementById("game");
    const ctx = canvas.getContext("2d");
    const livesEl = document.getElementById("lives");
    const scoreEl = document.getElementById("score");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let lives = 3;
    let score = 0;
    let roadOffset = 0;
    let gameActive = true;

    // Aracı ekranın biraz yukarısına aldık ki parmak altında kalarak kaybolmasın
    const player = { x: canvas.width / 2 - 30, y: canvas.height - 200, w: 60, h: 90 };
    let traffic = [];
    let hearts = [];

    // Dokunmatik Kontrol
    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        let touch = e.touches[0];
        player.x = touch.clientX - player.w / 2;
    }, { passive: false });

    function spawnTraffic() {
        if (gameActive && Math.random() < 0.03) {
            traffic.push({ x: Math.random() * (canvas.width - 60), y: -100, speed: 5 + (score/20) });
        }
    }

    function spawnHeart() {
        if (gameActive && Math.random() < 0.005) {
            hearts.push({ x: Math.random() * (canvas.width - 40), y: -50 });
        }
    }

    function draw() {
        if (!gameActive) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Yol ve Hareketli Çizgiler
        roadOffset += 10;
        ctx.strokeStyle = "rgba(255,255,255,0.7)";
        ctx.setLineDash([40, 40]);
        ctx.lineDashOffset = -roadOffset;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0); ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();

        // Kendi Aracın (Dik ve Düzgün)
        ctx.font = "70px Arial";
        ctx.save();
        ctx.translate(player.x + player.w/2, player.y + player.h/2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText("🏎️", -35, 25);
        ctx.restore();

        // Diğer Araçlar
        traffic.forEach((car, i) => {
            car.y += car.speed;
            ctx.save();
            ctx.translate(car.x + 30, car.y + 45);
            ctx.rotate(Math.PI / 2);
            ctx.fillText("🚘", -35, 25);
            ctx.restore();

            // Çarpışma Kontrolü
            if (player.x < car.x + 50 && player.x + 50 > car.x && player.y < car.y + 80 && player.y + 80 > car.y) {
                traffic.splice(i, 1);
                lives--;
                livesEl.innerText = lives;
                if (lives <= 0) { gameActive = false; alert("OYUN BİTTİ! Skor: " + score); location.reload(); }
            }
            if (car.y > canvas.height) { traffic.splice(i, 1); score += 10; scoreEl.innerText = score; }
        });

        // Can Toplama (❤️)
        hearts.forEach((h, i) => {
            h.y += 5;
            ctx.fillText("❤️", h.x, h.y + 40);
            if (player.x < h.x + 40 && player.x + 60 > h.x && player.y < h.y + 40 && player.y + 90 > h.y) {
                hearts.splice(i, 1);
                lives++;
                livesEl.innerText = lives;
            }
        });

        spawnTraffic();
        spawnHeart();
        requestAnimationFrame(draw);
    }
    draw();
</script>
</body>
</html>
"""

st.components.v1.html(oyun_html, height=1000)
