import os, sqlite3
from flask import Flask, request, redirect, session, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "istekli_sohbet_2026"
DB = "istek_sohbet.db"

# ---------------- 1. VERİ TABANI ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)")
        cur.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, username TEXT)")
init_db()

# ---------------- 2. GÖRSEL VE SİSTEM TASARIMI (HTML/JS) ----------------
UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Görüntülü İstek Paneli</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 280px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .video-area { display: flex; gap: 15px; width: 100%; justify-content: center; margin-top: 20px; }
        video { width: 45%; max-width: 450px; background: #000; border-radius: 15px; border: 2px solid #444; transform: scaleX(-1); }
        .user-card { background: #2c323a; padding: 12px; margin-bottom: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        button { padding: 8px 15px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .call-btn { background: #2ecc71; color: white; }
        .call-btn:disabled { background: #555; cursor: not-allowed; }
        #modal { display: none; position: fixed; top: 20%; left: 50%; transform: translate(-50%, -50%); background: #fff; color: #000; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 0 20px rgba(0,0,0,0.5); z-index: 100; }
        .status { margin: 10px; color: #f1c40f; }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerName">Biri arıyor...</h3>
        <button onclick="acceptCall()" style="background:green; color:white;">Kabul Et</button>
        <button onclick="rejectCall()" style="background:red; color:white;">Reddet</button>
    </div>

    <div class="sidebar">
        <h3>👥 Kişiler</h3>
        <div id="userList">Yükleniyor...</div>
    </div>

    <div class="main">
        <h2>Hoşgeldin, {{ session['username'] }}</h2>
        <div id="status" class="status">Kamera hazırlanıyor...</div>
        <div class="video-area">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
        <div style="margin-top:20px;">
            <button onclick="toggleMic()" id="micBtn" style="background:#555; color:white;">🎤 Sesi Kapat</button>
            <a href="/logout"><button style="background:none; color:gray;">Çıkış</button></a>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        const modal = document.getElementById('modal');
        let myStream, peer, incomingCall, myPeerId;
        let isCalling = false;

        const config = { config: { 'iceServers': [{ url: 'stun:stun.l.google.com:19302' }, { url: 'stun:global.stun.twilio.com:3478' }] } };

        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            peer = new Peer(config);

            peer.on('open', id => {
                myPeerId = id;
                statusDiv.innerText = "Online";
                fetch(`/register_peer?id=${id}`);
                updateList();
            });

            peer.on('call', call => {
                if(isCalling) return call.close(); // Zaten meşgulsen reddet
                incomingCall = call;
                document.getElementById('callerName').innerText = "Gelen Arama...";
                modal.style.display = 'block';
            });
        });

        async function updateList() {
            const res = await fetch('/get_online_users');
            const users = await res.json();
            const listDiv = document.getElementById('userList');
            listDiv.innerHTML = "";
            users.forEach(u => {
                if (u.peer_id !== myPeerId) {
                    listDiv.innerHTML += `<div class="user-card">
                        <span>${u.username}</span>
                        <button class="call-btn" id="btn-${u.peer_id}" onclick="startRequest('${u.peer_id}')">İstek Gönder</button>
                    </div>`;
                }
            });
        }

        function startRequest(pId) {
            if(isCalling) return;
            isCalling = true;
            document.getElementById(`btn-${pId}`).disabled = true;
            document.getElementById(`btn-${pId}`).innerText = "Bekleniyor...";
            
            statusDiv.innerText = "Arama İsteği Gönderildi...";
            const call = peer.call(pId, myStream);
            
            call.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
            });
            
            call.on('close', () => { resetCall(pId); });
        }

        function acceptCall() {
            modal.style.display = 'none';
            isCalling = true;
            incomingCall.answer(myStream);
            incomingCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
            });
        }

        function rejectCall() {
            modal.style.display = 'none';
            incomingCall.close();
            isCalling = false;
        }

        function resetCall(pId) {
            isCalling = false;
            statusDiv.innerText = "Arama Sonlandı.";
            const btn = document.getElementById(`btn-${pId}`);
            if(btn) { btn.disabled = false; btn.innerText = "İstek Gönder"; }
        }

        function toggleMic() {
            const enabled = myStream.getAudioTracks()[0].enabled;
            myStream.getAudioTracks()[0].enabled = !enabled;
            document.getElementById('micBtn').innerText = !enabled ? "🎤 Sesi Kapat" : "🎤 Sesi Aç";
        }

        setInterval(updateList, 8000);
    </script>
</body>
</html>
"""

# ---------------- 3. FLASK YOLLARI ----------------
@app.route('/')
def home():
    if "user_id" not in session: return redirect('/login')
    return render_template_string(UI_HTML)

@app.route('/register_peer')
def register_peer():
    pid = request.args.get('id')
    if pid and "username" in session:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR REPLACE INTO online_peers (peer_id, username) VALUES (?,?)", (pid, session["username"]))
    return "ok"

@app.route('/get_online_users')
def get_online_users():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT peer_id, username FROM online_peers")
        rows = cur.fetchall()
        return jsonify([{"peer_id": r[0], "username": r[1]} for r in rows])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['u']
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (u,))
            cur = con.cursor()
            cur.execute("SELECT id FROM users WHERE username=?", (u,))
            user = cur.fetchone()
            session["user_id"] = user[0]
            session["username"] = u
            return redirect('/')
    return '<body style="background:#0f1216;color:white;text-align:center;padding-top:100px;"><form method="post"><h2>Görüntülü Sohbet Giriş</h2><input name="u" placeholder="Adınız" required style="padding:10px;"><br><br><button style="padding:10px 20px;">Sisteme Gir</button></form></body>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
