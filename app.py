import streamlit as st

st.set_page_config(page_title="Araba Simülasyonu Pro", page_icon="🏎️", layout="wide")

# Ekranı temizleyen ve tam ekran yapan CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { overflow: hidden; height: 100vh; }
    iframe { width: 100vw; height: 100vh; border: none; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

oyun_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background: #333; font-family: 'Courier New', Courier, monospace; }
        canvas { display: block; touch-action: none; }
        #dashboard {
            position: absolute; bottom: 20px; left: 20px; color: #0f0; 
            background: rgba(0,0,0,0.7); padding: 15px; border-radius: 10px;
            border: 2px solid #0f0; pointer-events: none;
        }
        #top-bar {
            position: absolute; top: 10px; width: 100%; display: flex;
            justify-content: space-around; color: white; font-size: 20px;
        }
    </style>
</head>
<body>
    <div id="top-bar">
        <span>❤️ Can: <b id="lives">3</b></span>
        <span>🏆 Skor: <b id="score">0</b></span>
    </div>
    <div id="dashboard">
        <div>HIZ: <span id="speed">0</span> KM/H</div>
        <div id="gear">VİTES: 1</div>
    </div>
    <canvas id="simCanvas"></canvas>

<script>
    const canvas = document.getElementById("simCanvas");
    const ctx = canvas.getContext("2d");
    const speedEl = document.getElementById("speed");
    const livesEl = document.getElementById("lives");
    const scoreEl = document.getElementById("score");
    const gearEl = document.getElementById("gear");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let lives = 3;
    let score = 0;
    let speed = 0;
    let maxSpeed = 220;
    let gameActive = true;
    let roadPos = 0;

    const player = { x: canvas.width / 2, y: canvas.height - 180, w: 60, h: 100, targetX: canvas.width / 2 };

    let traffic = [];

    // Dokunmatik Simülasyon Kontrolü
    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        player.targetX = e.touches[0].clientX - player.w / 2;
    }, { passive: false });

    function createTraffic() {
        if (Math.random() < 0.02) {
            traffic.push({ x: Math.random() * (canvas.width - 60), y: -120, speed: 3 + Math.random() * 5 });
        }
    }

    function update() {
        if (!gameActive) return;

        // Hızlanma simülasyonu
        if (speed < maxSpeed) speed += 0.2;
        speedEl.innerText = Math.floor(speed);
        gearEl.innerText = "VİTES: " + (Math.floor(speed / 50) + 1);

        // Aracın yumuşak dönüşü (Simülasyon hissi)
        player.x += (player.targetX - player.x) * 0.1;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Yol Çizimi
        roadPos += speed * 0.1;
        ctx.fillStyle = "#444";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = "white";
        ctx.setLineDash([50, 50]);
        ctx.lineDashOffset = -roadPos;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0); ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();

        // Kendi Aracın (F1 Simülatörü)
        ctx.font = "70px Arial";
        ctx.save();
        ctx.translate(player.x + player.w/2, player.y + player.h/2);
        // Dönüşe göre hafif eğim ver
        let tilt = (player.targetX - player.x) * 0.01;
        ctx.rotate(-Math.PI / 2 + tilt);
        ctx.fillText("🏎️", -35, 25);
        ctx.restore();

        // Trafik
        traffic.forEach((car, i) => {
            car.y += (speed * 0.05) + car.speed;
            ctx.save();
            ctx.translate(car.x + 30, car.y + 50);
            ctx.rotate(Math.PI / 2);
            ctx.fillText("🚘", -35, 25);
            ctx.restore();

            // Çarpışma
            if (Math.abs(player.x - car.x) < 50 && Math.abs(player.y - car.y) < 80) {
                traffic.splice(i, 1);
                lives--;
                speed = 20; // Çarpınca yavaşla
                livesEl.innerText = lives;
                if (lives <= 0) { alert("SİMÜLASYON BİTTİ! Skor: " + score); location.reload(); }
            }

            if (car.y > canvas.height) { traffic.splice(i, 1); score += 10; scoreEl.innerText = score; }
        });

        createTraffic();
        requestAnimationFrame(update);
    }
    update();
</script>
</body>
</html>
