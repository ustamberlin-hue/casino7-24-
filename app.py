import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "sohbet_chat_v7"
DB = "sohbet_v7.db"

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
    <title>Görüntülü Sohbet & Mesaj v7</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 280px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; display: flex; flex-direction: column; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; overflow-y: auto; }
        .video-area { display: flex; gap: 15px; width: 100%; justify-content: center; margin-top: 10px; }
        video { width: 45%; max-width: 400px; background: #000; border-radius: 12px; border: 2px solid #444; transform: scaleX(-1); }
        
        /* Sohbet Alanı */
        #chatBox { width: 90%; max-width: 800px; height: 200px; background: #1a1e23; border: 1px solid #444; margin-top: 20px; border-radius: 10px; display: flex; flex-direction: column; }
        #messages { flex: 1; overflow-y: auto; padding: 10px; font-size: 14px; }
        .msg { margin-bottom: 5px; padding: 5px 10px; border-radius: 5px; background: #2c323a; }
        #chatInputArea { display: flex; border-top: 1px solid #444; }
        #chatInput { flex: 1; background: none; border: none; color: white; padding: 10px; outline: none; }
        
        .user-card { background: #2c323a; padding: 10px; margin-bottom: 8px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        button { padding: 8px 12px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .call-btn { background: #2ecc71; color: white; }
        .cancel-btn { background: #e74c3c !important; color: white; }
        #modal { display: none; position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%); background: #fff; color: #000; padding: 30px; border-radius: 10px; text-align: center; z-index: 2000; box-shadow: 0 0 40px rgba(0,0,0,0.8); }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerName">Arama Geliyor...</h3>
        <button onclick="acceptCall()" style="background:green; color:white; padding:10px 20px;">KABUL ET</button>
        <button onclick="rejectCall()" style="background:red; color:white; padding:10px 20px; margin-left:10px;">REDDET</button>
    </div>

    <div class="sidebar">
        <h3>🟢 Aktif Kişiler</h3>
        <div id="userList" style="flex:1;"></div>
        <a href="/logout" style="color:gray; text-decoration:none; font-size:12px; margin-top:10px;">Çıkış Yap</a>
    </div>

    <div class="main">
        <h3>Kullanıcı: {{ session['username'] }}</h3>
        <div id="status" style="color:#f1c40f; font-weight:bold; margin-bottom:10px;">Sistem Hazır</div>
        
        <div class="video-area">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>

        <button onclick="endCall()" id="endBtn" class="cancel-btn" style="display:none; margin-top:10px;">📞 Aramayı Kapat</button>

        <div id="chatBox">
            <div id="messages"></div>
            <div id="chatInputArea">
                <input type="text" id="chatInput" placeholder="Mesaj yazın..." onkeypress="checkEnter(event)">
                <button onclick="sendMessage()" style="background:#3498db; color:white;">Gönder</button>
            </div>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        const messagesDiv = document.getElementById('messages');
        const modal = document.getElementById('modal');
        let myStream, peer, currentCall, conn, myPeerId;
        let isBusy = false;

        const peerConfig = {
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
            peer = new Peer(peerConfig);

            peer.on('open', id => {
                myPeerId = id;
                heartbeat(id);
                updateList();
            });

            // Gelen Veri Bağlantısı (Sohbet ve Komutlar)
            peer.on('connection', c => {
                conn = c;
                setupChat();
            });

            // Gelen Arama
            peer.on('call', call => {
                currentCall = call;
                modal.style.display = 'block';
                currentCall.on('close', () => cleanUI());
            });
        });

        function setupChat() {
            conn.on('data', data => {
                if(data.type === 'msg') {
                    addMessage(conn.metadata.user, data.text);
                } else if (data.type === 'reject' || data.type === 'end') {
                    cleanUI();
                }
            });
            conn.on('close', () => cleanUI());
        }

        function makeCall(pId) {
            isBusy = true;
            statusDiv.innerText = "Aranıyor...";
            document.getElementById('endBtn').style.display = 'inline-block';
            
            // Hem arama hem sohbet bağlantısı kur
            conn = peer.connect(pId, { metadata: { user: "{{ session['username'] }}" } });
            setupChat();
            
            currentCall = peer.call(pId, myStream);
            currentCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
            });
            currentCall.on('close', () => cleanUI());
            updateList();
        }

        function acceptCall() {
            modal.style.display = 'none';
            isBusy = true;
            document.getElementById('endBtn').style.display = 'inline-block';
            currentCall.answer(myStream);
            currentCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlandı!";
            });
            updateList();
        }

        function rejectCall() {
            if(conn) conn.send({type: 'reject'});
            modal.style.display = 'none';
            cleanUI();
        }

        function endCall() {
            if(conn) conn.send({type: 'end'});
            if(currentCall) currentCall.close();
            cleanUI();
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            if(conn && input.value) {
                conn.send({type: 'msg', text: input.value});
                addMessage("Ben", input.value);
                input.value = "";
            }
        }

        function addMessage(user, text) {
            const div = document.createElement('div');
            div.className = 'msg';
            div.innerHTML = `<b>${user}:</b> ${text}`;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function checkEnter(e) { if(e.key === 'Enter') sendMessage(); }

        function cleanUI() {
            isBusy = false;
            remoteVideo.srcObject = null;
            statusDiv.innerText = "Bağlantı Kesildi.";
            document.getElementById('endBtn').style.display = 'none';
            modal.style.display = 'none';
            updateList();
        }

        function heartbeat(id) {
            fetch(`/register_peer?id=${id}`);
            setTimeout(() => heartbeat(id), 4000);
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
                            <button class="${isBusy ? 'cancel-btn' : 'call-btn'}" 
                                    onclick="${isBusy ? 'endCall()' : `makeCall('${u.peer_id}')`}">
                                ${isBusy ? 'İptal' : 'Ara'}
                            </button>
                        </div>`;
                }
            });
        }
        setInterval(updateList, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if "username" not in session: return redirect('/login')
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
        con.execute("DELETE FROM online_peers WHERE last_seen < ?", (now - 10,))
        cur = con.cursor()
        cur.execute("SELECT peer_id, username FROM online_peers")
        return jsonify([{"peer_id": r[0], "username": r[1]} for r in cur.fetchall()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['u']
        session["username"] = u
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
