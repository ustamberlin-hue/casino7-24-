import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "sohbet_cozum_v5"
DB = "sohbet_v5.db"

def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, username TEXT, last_seen REAL)")
init_db()

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Görüntülü Sohbet v5</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 280px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .video-area { display: flex; gap: 15px; width: 100%; justify-content: center; margin-top: 20px; }
        video { width: 45%; max-width: 450px; background: #000; border-radius: 15px; border: 2px solid #444; transform: scaleX(-1); }
        .user-card { background: #2c323a; padding: 12px; margin-bottom: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        button { padding: 8px 15px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .call-btn { background: #2ecc71; color: white; }
        .cancel-btn { background: #e74c3c !important; color: white; }
        #modal { display: none; position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%); background: #fff; color: #000; padding: 30px; border-radius: 10px; text-align: center; z-index: 1000; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .status { margin: 10px; color: #f1c40f; font-weight: bold; }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerName">Arama Geliyor...</h3>
        <button onclick="acceptCall()" style="background:green; color:white; padding:12px 25px;">Kabul Et</button>
        <button onclick="rejectCall()" style="background:red; color:white; padding:12px 25px;">Reddet</button>
    </div>

    <div class="sidebar">
        <h3>🟢 Aktif Kişiler</h3>
        <div id="userList"></div>
    </div>

    <div class="main">
        <h2>{{ session['username'] }}</h2>
        <div id="status" class="status">Sistem Hazır</div>
        <div class="video-area">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
        <div style="margin-top:20px;">
            <button onclick="endCall()" id="endBtn" class="cancel-btn" style="display:none; padding:12px 30px;">📞 Aramayı Kapat</button>
            <a href="/logout"><button style="background:none; color:gray; margin-left:20px;">Çıkış</button></a>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        const modal = document.getElementById('modal');
        let myStream, peer, currentCall, myPeerId;
        let isCalling = false;

        // Bağlantıyı zorlayan ayarlar (STUN/ICE)
        const peerOptions = {
            config: { 
                'iceServers': [
                    { url: 'stun:stun.l.google.com:19302' }, 
                    { url: 'stun:stun1.l.google.com:19302' },
                    { url: 'stun:global.stun.twilio.com:3478' }
                ],
                'sdpSemantics': 'unified-plan'
            }
        };

        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            peer = new Peer(peerOptions);

            peer.on('open', id => {
                myPeerId = id;
                heartbeat(id);
                updateList();
            });

            peer.on('call', call => {
                if(isCalling) { call.answer(); setTimeout(() => call.close(), 500); return; }
                currentCall = call;
                modal.style.display = 'block';
                setupCallEvents(call);
            });
        });

        function setupCallEvents(call) {
            call.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
                isCalling = true;
                document.getElementById('endBtn').style.display = 'inline-block';
                updateList();
            });
            call.on('close', () => cleanUI());
            call.on('error', () => cleanUI());
        }

        function makeCall(pId) {
            isCalling = true;
            statusDiv.innerText = "Aranıyor...";
            updateList();
            currentCall = peer.call(pId, myStream);
            setupCallEvents(currentCall);
        }

        function acceptCall() {
            modal.style.display = 'none';
            currentCall.answer(myStream);
            setupCallEvents(currentCall);
        }

        function endCall() {
            if(currentCall) currentCall.close();
            cleanUI();
        }

        function rejectCall() {
            modal.style.display = 'none';
            if(currentCall) currentCall.close();
            cleanUI();
        }

        function cleanUI() {
            isCalling = false;
            remoteVideo.srcObject = null;
            statusDiv.innerText = "Bağlantı Kesildi.";
            document.getElementById('endBtn').style.display = 'none';
            modal.style.display = 'none';
            updateList();
        }

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
                                    onclick="${isCalling ? 'endCall()' : `makeCall('${u.peer_id}')`}">
                                ${isCalling ? 'İptal Et' : 'Ara'}
                            </button>
                        </div>`;
                }
            });
        }
        setInterval(updateList, 6000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if "user_id" not in session: return redirect('/login')
    return render_template_string(UI_HTML)

@app.route('/register_peer')
def register_peer():
    pid = request.args.get('id')
    if pid and "username" in session:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR REPLACE INTO online_peers (peer_id, username, last_seen) VALUES (?,?,?)", 
                        (pid, session["username"], time.time()))
    return "ok"

@app.route('/get_online_users')
def get_online_users():
    now = time.time()
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM online_peers WHERE last_seen < ?", (now - 12,))
        cur = con.cursor()
        cur.execute("SELECT peer_id, username FROM online_peers")
        return jsonify([{"peer_id": r[0], "username": r[1]} for r in cur.fetchall()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['u']
        session["user_id"], session["username"] = u, u
        return redirect('/')
    return '<body style="background:#0f1216;color:white;text-align:center;padding-top:100px;"><form method="post"><h2>Giriş</h2><input name="u" placeholder="Adınız" required><br><br><button>Gir</button></form></body>'

@app.route('/logout')
def logout():
    if "username" in session:
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM online_peers WHERE username=?", (session["username"],))
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
