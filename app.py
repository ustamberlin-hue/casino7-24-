import os, sqlite3
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "full_chat_single_file_2026"
DB = "chat.db"

# ---------------- 1. VERİ TABANI AYARI ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, user_id INTEGER)")
init_db()

# ---------------- 2. GÖRSEL VE BAĞLANTI TASARIMI (HTML/CSS/JS) ----------------
# Bu bölüm hem tasarımı hem de farklı internetlerde çalışmayı sağlayan STUN ayarlarını içerir.
UI_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Görüntülü Sohbet - Canlı</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0b0e11; color: #e9eaeb; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 15px; }
        .header { background: #1e2329; padding: 15px; border-radius: 0 0 20px 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px; }
        .video-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }
        video { width: 45%; max-width: 450px; min-width: 300px; height: 340px; background: #000; border-radius: 15px; border: 3px solid #3498db; object-fit: cover; transform: scaleX(-1); }
        .controls { margin-top: 30px; display: flex; justify-content: center; gap: 15px; }
        button { padding: 15px 30px; border-radius: 50px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 16px; }
        .btn-next { background: #f0b90b; color: #000; }
        .btn-mute { background: #474d57; color: white; }
        .active-mute { background: #e74c3c !important; }
        #status { margin: 10px; font-weight: bold; color: #2ecc71; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎥 Rastgele Görüntülü Sohbet</h1>
        <div id="status">Kamera İzni Bekleniyor...</div>
    </div>

    <div class="video-grid">
        <video id="localVideo" autoplay playsinline muted></video>
        <video id="remoteVideo" autoplay playsinline></video>
    </div>

    <div class="controls">
        <button id="muteBtn" class="btn-mute" onclick="toggleMute()">🎤 Sesi Kapat</button>
        <button class="btn-next" onclick="matchNext()">🎲 SONRAKİ KİŞİ</button>
        <a href="/logout"><button style="background:none; color:gray;">Çıkış Yap</button></a>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusMsg = document.getElementById('status');
        let myStream, peer, currentCall;
        let muted = false;

        // --- STUN SUNUCULARI: Farklı internetlerde görüntünün gitmesini sağlar ---
        const config = {
            config: {
                'iceServers': [
                    { url: 'stun:stun.l.google.com:19302' },
                    { url: 'stun:stun1.l.google.com:19302' },
                    { url: 'stun:stun2.l.google.com:19302' }
                ]
            }
        };

        // Kamerayı Başlat
        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            statusMsg.innerText = "Kamera Aktif. Bağlanıyor...";

            peer = new Peer(config);

            peer.on('open', (id) => {
                statusMsg.innerText = "Bağlanmaya Hazır!";
                fetch('/register_peer?id=' + id);
            });

            // Gelen Aramayı Yakala
            peer.on('call', (call) => {
                statusMsg.innerText = "Birine Bağlandın!";
                call.answer(myStream);
                call.on('stream', (remoteStream) => {
                    remoteVideo.srcObject = remoteStream;
                });
                currentCall = call;
            });
        }).catch(err => {
            statusMsg.innerText = "Hata: Kameraya ulaşılamadı!";
            console.error(err);
        });

        // Rastgele Eşleş
        async function matchNext() {
            statusMsg.innerText = "Yeni Biri Aranıyor...";
            const response = await fetch('/get_random_peer');
            const data = await response.json();

            if (data.peer_id && data.peer_id !== peer.id) {
                if (currentCall) currentCall.close();
                const call = peer.call(data.peer_id, myStream);
                call.on('stream', (remoteStream) => {
                    remoteVideo.srcObject = remoteStream;
                    statusMsg.innerText = "Yeni Birine Bağlandın!";
                });
                currentCall = call;
            } else {
                statusMsg.innerText = "Şu an kimse yok, biraz bekle ve tekrar dene!";
            }
        }

        // Ses Kapama/Açma
        function toggleMute() {
            muted = !muted;
            myStream.getAudioTracks()[0].enabled = !muted;
            const btn = document.getElementById('muteBtn');
            btn.innerText = muted ? "🎤 Sesi Aç" : "🎤 Sesi Kapat";
            btn.classList.toggle('active-mute', muted);
        }
    </script>
</body>
</html>
"""

# ---------------- 3. SUNUCU YÖNLENDİRMELERİ (FLASK) ----------------
@app.route('/')
def home():
    if "user_id" not in session: return redirect('/login')
    return render_template_string(UI_HTML)

@app.route('/register_peer')
def register_peer():
    pid = request.args.get('id')
    if pid and "user_id" in session:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR REPLACE INTO online_peers (peer_id, user_id) VALUES (?,?)", (pid, session["user_id"]))
    return "ok"

@app.route('/get_random_peer')
def get_random_peer():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        # Kendisi dışındaki rastgele birini getir
        cur.execute("SELECT peer_id FROM online_peers WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (session.get("user_id", 0),))
        res = cur.fetchone()
        return {"peer_id": res[0] if res else None}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['u'], request.form['p']
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            user = cur.fetchone()
            if not user:
                con.execute("INSERT INTO users (username, password) VALUES (?,?)", (u, p))
                cur.execute("SELECT * FROM users WHERE username=?", (u,))
                user = cur.fetchone()
            session["user_id"] = user[0]
            return redirect('/')
    return '<body style="background:#0b0e11; color:white; text-align:center;"><br><h2>Giriş / Kayıt</h2><form method="post"><input name="u" placeholder="Kullanıcı Adı" required><br><br><input name="p" type="password" placeholder="Şifre" required><br><br><button type="submit">Giriş Yap</button></form></body>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
