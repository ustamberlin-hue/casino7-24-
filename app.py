import streamlit as st

st.set_page_config(page_title="Hızlı Şoför", page_icon="🏎️")

st.title("🏎️ Trafik Canavarı: Kaçış")
st.write("Ekrana dokunarak veya ok tuşlarıyla arabayı yönlendir. Diğer araçlara çarpma!")

# Oyunun JavaScript ve HTML motoru
oyun_html = """
<div id="game-container" style="text-align:center;">
    <canvas id="gameCanvas" width="300" height="400" style="border:5px solid #333; background:#555; touch-action:none;"></canvas>
    <div style="margin-top:10px;">
        <button onclick="moveLeft()" style="padding:15px; font-size:20px;">⬅️ Sol</button>
        <button onclick="moveRight()" style="padding:15px; font-size:20px;">Sağ ➡️</button>
    </div>
    <h2 id="scoreBoard">Skor: 0</h2>
</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const scoreBoard = document.getElementById("scoreBoard");

    let player = { x: 125, y: 330, w: 50, h: 60, color: "red" };
    let enemies = [];
    let score = 0;
    let gameActive = true;

    function drawPlayer() {
        ctx.fillStyle = player.color;
        ctx.fillRect(player.x, player.y, player.w, player.h);
        // Farlar
        ctx.fillStyle = "yellow";
        ctx.fillRect(player.x + 5, player.y, 10, 5);
        ctx.fillRect(player.x + 35, player.y, 10, 5);
    }

    function createEnemy() {
        if (Math.random() < 0.02) {
            enemies.push({ x: Math.random() * 250, y: -50, w: 50, h: 60, speed: 3 + (score/10) });
        }
    }

    function drawEnemies() {
        ctx.fillStyle = "blue";
        enemies.forEach((en, index) => {
            ctx.fillRect(en.x, en.y, en.w, en.h);
            en.y += en.speed;

            // Çarpışma Kontrolü
            if (player.x < en.x + en.w && player.x + player.w > en.x &&
                player.y < en.y + en.h && player.y + player.h > en.y) {
                gameActive = false;
                alert("KAZA YAPTIN! Skorun: " + score);
                document.location.reload();
            }

            if (en.y > 400) {
                enemies.splice(index, 1);
                score++;
                scoreBoard.innerHTML = "Skor: " + score;
            }
        });
    }

    function moveLeft() { if (player.x > 0) player.x -= 25; }
    function moveRight() { if (player.x < 250) player.x += 25; }

    // Klavye Desteği
    window.addEventListener("keydown", e => {
        if (e.key === "ArrowLeft") moveLeft();
        if (e.key === "ArrowRight") moveRight();
    });

    function update() {
        if (!gameActive) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Yol çizgileri
        ctx.strokeStyle = "white";
        ctx.setLineDash([20, 20]);
        ctx.beginPath();
        ctx.moveTo(150, 0); ctx.lineTo(150, 400);
        ctx.stroke();

        drawPlayer();
        createEnemy();
        drawEnemies();
        requestAnimationFrame(update);
    }
    update();
</script>
"""

st.components.v1.html(oyun_html, height=600)

st.divider()
st.info("💡 **Tüyo:** Skorun arttıkça karşıdan gelen arabalar hızlanacak! Gözünü yoldan ayırma.")
