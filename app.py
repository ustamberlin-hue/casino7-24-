import os, sqlite3
from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "rastgele_sohbet_secret_2026"
DB = "chat.db"

# ---------------- 1. VERİ TABANI (Kullanıcı ve Aktif Peer Listesi) ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
        # Aktif kullanıcıların Peer ID'lerini tutan tablo
        cur.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, user_id INTEGER)")
init_db()

# ---------------- 2. GÖRSEL TASARIM (HTML/JS) ----------------
SOHBET_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Rastgele Görüntülü Sohbet</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 10px; }
        .video-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-top: 20px; }
        video { width: 45%; max-width: 400px; background: #000; border-radius: 15px; border: 2px solid #3498db; transform: scaleX(-1); }
        .controls { margin-top: 25px; display: flex; justify-content: center; gap: 10px; }
        button { padding: 12px 25px; border-radius: 30px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-next { background: #e67e22; color: white; font-size: 18px; }
        .btn-mute { background: #95a5a6; color: white; }
        .muted { background: #e74c3c !important; }
        .status { color: #2ecc71; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🌟 Rastgele Sohbet Odası</h1>
    <div id="status" class="status">Kamera hazırlanıyor...</div>

    <div class="video-container">
        <video id="localVideo" autoplay playsinline muted></video>
        <video id="remoteVideo" autoplay playsinline></video>
    </div>

    <div class="controls">
        <button id="muteBtn" class="btn-mute" onclick="toggleAudio()">🎤 Sesi Kapat</button>
        <button class="btn-next" onclick="findRandomPerson()">🎲 SONRAKİ KİŞİ</button>
        <a href="/logout"><button style="background:none; color:gray;">Çıkış</button></a>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        let myStream, peer, currentCall;
        let isMuted = false;

        // 1. Kamerayı Başlat ve Peer ID Al
        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            
            peer = new Peer(); 
            peer.on('open', (id) => {
                statusDiv.innerText = "Bağlanmaya hazır!";
                // Peer ID'yi sunucuya kaydet
                fetch('/register_peer?id=' + id);
            });

            // 2. Gelen aramaları otomatik kabul et
            peer.on('call', (call) => {
                currentCall = call;
                call.answer(myStream);
                call.on('stream', (remoteStream) => {
                    remoteVideo.srcObject = remoteStream;
                    statusDiv.innerText = "Birine bağlandın!";
                });
            });
        });

        // 3. Rastgele Birini Bul ve Ara
        async function findRandomPerson() {
            statusDiv.innerText = "Aranıyor...";
            const res = await fetch('/get_random_peer');
            const data = await res.json();
            
            if (data.peer_id && data.peer_id !== peer.id) {
                if (currentCall) currentCall.close();
                const call = peer.call(data.peer_id, myStream);
                currentCall = call;
                call.on('stream', (remoteStream) => {
                    remoteVideo.srcObject = remoteStream;
                    statusDiv.innerText = "Yeni birine bağlandın!";
                });
            } else {
                statusDiv.innerText = "Şu an kimse yok, tekrar dene!";
            }
        }

        // 4. Ses Aç/Kapat
        function toggleAudio() {
            isMuted = !isMuted;
            myStream.getAudioTracks()[0].enabled = !isMuted;
            const btn = document.getElementById('muteBtn');
            btn.innerText = isMuted ? "🎤 Sesi Aç" : "🎤 Sesi Kapat";
            btn.classList.toggle('muted', isMuted);
        }
    </script>
</body>
</html>
"""

# ---------------- 3. ROUTES ----------------
@app.route('/')
def index():
    if "user_id" not in session: return redirect('/login')
    return render_template_string(SOHBET_HTML)

@app.route('/register_peer')
def register_peer():
    peer_id = request.args.get('id')
    if peer_id and "user_id" in session:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR REPLACE INTO online_peers (peer_id, user_id) VALUES (?,?)", (peer_id, session["user_id"]))
    return "ok"

@app.route('/get_random_peer')
def get_random_peer():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        # Kendisi hariç rastgele bir aktif kullanıcı seç
        cur.execute("SELECT peer_id FROM online_peers WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (session.get("user_id", 0),))
        row = cur.fetchone()
        return {"peer_id": row[0] if row else None}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['u'], request.form['p']
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            user = cur.fetchone()
            if not user: # Kullanıcı yoksa oluştur (Pratik olması için)
                con.execute("INSERT INTO users (username, password) VALUES (?,?)", (u, p))
                cur.execute("SELECT * FROM users WHERE username=?", (u,))
                user = cur.fetchone()
            session["user_id"] = user[0]
            return redirect('/')
    return '<h2>Giriş / Kayıt</h2><form method="post"><input name="u" placeholder="Kullanıcı"><br><input name="p" type="password" placeholder="Şifre"><br><button>Giriş Yap</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
