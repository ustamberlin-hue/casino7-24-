import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "sohbet_pro_v3_2026"
DB = "sohbet_v3.db"

# ---------------- 1. VERİ TABANI ----------------
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)")
        # last_seen ekleyerek aktif olmayanları temizleyeceğiz
        cur.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, username TEXT, last_seen REAL)")
init_db()

# ---------------- 2. GÖRSEL VE SİSTEM TASARIMI (HTML/JS) ----------------
UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Görüntülü Arama Sistemi</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; overflow-y: auto; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .video-area { display: flex; gap: 15px; width: 100%; justify-content: center; margin-top: 20px; }
        video { width: 45%; max-width: 450px; background: #000; border-radius: 15px; border: 2px solid #444; transform: scaleX(-1); }
        .user-card { background: #2c323a; padding: 12px; margin-bottom: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        button { padding: 8px 15px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .call-btn { background: #2ecc71; color: white; }
        .cancel-btn { background: #e74c3c !important; color: white; }
        #modal { display: none; position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%); background: #fff; color: #000; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 0 30px rgba(0,0,0,0.7); z-index: 1000; }
        .status { margin: 10px; color: #f1c40f; font-weight: bold; }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerName">Arama Geliyor...</h3>
        <button onclick="acceptCall()" style="background:green; color:white; padding:15px;">Kabul Et</button>
        <button onclick="rejectCall()" style="background:red; color:white; padding:15px;">Reddet</button>
    </div>

    <div class="sidebar">
        <h3>🟢 Aktif Kişiler</h3>
        <div id="userList">Yükleniyor...</div>
    </div>

    <div class="main">
        <h2>Kullanıcı: {{ session['username'] }}</h2>
        <div id="status" class="status">Sistem Hazırlanıyor...</div>
        <div class="video-area">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
        <div style="margin-top:20px;">
            <button onclick="toggleMic()" id="micBtn" style="background:#474d57; color:white;">🎤 Sesi Kapat</button>
            <button onclick="endCurrentCall()" style="background:#e74c3c; color:white;">📞 Aramayı Kapat</button>
            <a href="/logout"><button style="background:none; color:gray; margin-left:20px;">Çıkış Yap</button></a>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        const modal = document.getElementById('modal');
        let myStream, peer, incomingCall, outgoingCall, myPeerId;
        let isCalling = false;

        const config = { 
            config: { 
                'iceServers': [
                    { url: 'stun:stun.l.google.com:19302' }, 
                    { url: 'stun:global.stun.twilio.com:3478' }
                ],
                'iceCandidatePoolSize': 10
            } 
        };

        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            peer = new Peer(config);

            peer.on('open', id => {
                myPeerId = id;
                statusDiv.innerText = "Sohbete Hazır";
                heartbeat(id);
                updateList();
            });

            peer.on('call', call => {
                if(isCalling) { call.answer(); call.close(); return; }
                incomingCall = call;
                modal.style.display = 'block';
            });
        });

        // Online kalmak için sunucuya her 5 saniyede bir sinyal gönderir
        function heartbeat(id) {
            fetch(`/register_peer?id=${id}`);
            setTimeout(() => heartbeat(id), 5000);
        }

        async function updateList() {
            const res = await fetch('/get_online_users');
            const users = await res.json();
            const listDiv = document.getElementById('userList');
            listDiv.innerHTML = "";
            users.forEach(u => {
                if (u.peer_id !== myPeerId) {
                    listDiv.innerHTML += `
                        <div class="user-card">
                            <span>${u.username}</span>
                            <button class="${isCalling ? 'cancel-btn' : 'call-btn'}" 
                                    id="btn-${u.peer_id}" 
                                    onclick="${isCalling ? 'cancelCall()' : `sendRequest('${u.peer_id}')`}">
                                ${isCalling ? 'İptal Et' : 'İstek Gönder'}
                            </button>
                        </div>`;
                }
            });
        }

        function sendRequest(pId) {
            isCalling = true;
            statusDiv.innerText = "Arama İsteği Gönderildi...";
            updateList();
            
            outgoingCall = peer.call(pId, myStream);
            outgoingCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
            });
            outgoingCall.on('close', () => { cancelCall(); });
        }

        function cancelCall() {
            if(outgoingCall) outgoingCall.close();
            if(incomingCall) incomingCall.close();
            remoteVideo.srcObject = null;
            isCalling = false;
            statusDiv.innerText = "Arama İptal Edildi.";
            updateList();
        }

        function acceptCall() {
            modal.style.display = 'none';
            isCalling = true;
            incomingCall.answer(myStream);
            incomingCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
                updateList();
            });
        }

        function rejectCall() {
            modal.style.display = 'none';
            incomingCall.close();
            isCalling = false;
        }

        function endCurrentCall() { cancelCall(); }

        function toggleMic() {
            const enabled = myStream.getAudioTracks()[0].enabled;
            myStream.getAudioTracks()[0].enabled = !enabled;
            document.getElementById('micBtn').innerText = !enabled ? "🎤 Sesi Kapat" : "🎤 Sesi Aç";
        }

        setInterval(updateList, 6000);
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
            # last_seen süresini günceller
            con.execute("INSERT OR REPLACE INTO online_peers (peer_id, username, last_seen) VALUES (?,?,?)", 
                        (pid, session["username"], time.time()))
    return "ok"

@app.route('/get_online_users')
def get_online_users():
    now = time.time()
    with sqlite3.connect(DB) as con:
        # 10 saniye boyunca sinyal vermeyeni listeden siler
        con.execute("DELETE FROM online_peers WHERE last_seen < ?", (now - 10,))
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
    return '<body style="background:#0f1216;color:white;text-align:center;padding-top:100px;"><form method="post"><h2>Sohbet Paneli Giriş</h2><input name="u" placeholder="Adınız" required style="padding:10px;"><br><br><button style="padding:10px 20px;">Giriş Yap</button></form></body>'

@app.route('/logout')
def logout():
    if "username" in session:
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM online_peers WHERE username=?", (session["username"],))
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
