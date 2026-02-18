import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "sohbet_kesin_cozum_v6"
DB = "sohbet_v6.db"

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
    <title>Görüntülü Sohbet v6</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 280px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; position: relative; }
        .video-area { display: flex; gap: 15px; width: 100%; justify-content: center; margin-top: 20px; }
        video { width: 45%; max-width: 450px; background: #000; border-radius: 15px; border: 2px solid #444; transform: scaleX(-1); }
        .user-card { background: #2c323a; padding: 12px; margin-bottom: 10px; border-radius: 8px; display: flex; justify-content: space-between; }
        button { padding: 8px 15px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .call-btn { background: #2ecc71; color: white; }
        .cancel-btn { background: #e74c3c !important; color: white; }
        #modal { display: none; position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%); background: #fff; color: #000; padding: 30px; border-radius: 10px; text-align: center; z-index: 2000; box-shadow: 0 0 40px rgba(0,0,0,0.8); }
        .status { margin: 10px; color: #f1c40f; font-weight: bold; }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerName">Arama Geliyor...</h3>
        <button onclick="acceptCall()" style="background:green; color:white; padding:15px 30px; font-size:18px;">KABUL ET</button>
        <button onclick="rejectCall()" style="background:red; color:white; padding:15px 30px; font-size:18px; margin-left:10px;">REDDET</button>
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
            <button onclick="endCall()" id="endBtn" class="cancel-btn" style="display:none; padding:12px 40px;">📞 Aramayı Kapat / İptal Et</button>
            <a href="/logout"><button style="background:none; color:gray; margin-left:20px;">Çıkış</button></a>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const statusDiv = document.getElementById('status');
        const modal = document.getElementById('modal');
        let myStream, peer, currentCall, myPeerId;
        let isBusy = false;

        const peerConfig = {
            config: { 
                'iceServers': [
                    { url: 'stun:stun.l.google.com:19302' },
                    { url: 'stun:stun1.l.google.com:19302' },
                    { url: 'stun:stun2.l.google.com:19302' },
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

            peer.on('call', call => {
                if(isBusy) { 
                    call.answer(); 
                    setTimeout(() => call.close(), 500); 
                    return; 
                }
                currentCall = call;
                modal.style.display = 'block';
                
                // Reddetme veya Kapatma sinyalini dinle
                currentCall.on('close', () => cleanUI());
                currentCall.on('error', () => cleanUI());
            });
        }).catch(err => {
            alert("Kamera izni gerekli!");
            statusDiv.innerText = "Kamera Hatası!";
        });

        function makeCall(pId) {
            isBusy = true;
            statusDiv.innerText = "Aranıyor...";
            document.getElementById('endBtn').style.display = 'inline-block';
            
            currentCall = peer.call(pId, myStream);
            
            currentCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlantı Kuruldu!";
            });
            
            currentCall.on('close', () => cleanUI());
            currentCall.on('error', () => cleanUI());
            updateList();
        }

        function acceptCall() {
            modal.style.display = 'none';
            isBusy = true;
            document.getElementById('endBtn').style.display = 'inline-block';
            
            currentCall.answer(myStream);
            
            currentCall.on('stream', rStream => {
                remoteVideo.srcObject = rStream;
                statusDiv.innerText = "Bağlantı Kuruldu!";
            });
            
            currentCall.on('close', () => cleanUI());
            updateList();
        }

        function rejectCall() {
            if(currentCall) {
                currentCall.answer(); // Bağlantıyı kısa süreli aç
                setTimeout(() => currentCall.close(), 100); // Hemen kapat (karşıya sinyal gider)
            }
            modal.style.display = 'none';
            cleanUI();
        }

        function endCall() {
            if(currentCall) currentCall.close();
            cleanUI();
        }

        function cleanUI() {
            isBusy = false;
            remoteVideo.srcObject = null;
            statusDiv.innerText = "Bağlantı Sonlandı.";
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
                                ${isBusy ? 'İptal Et' : 'Ara'}
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
        con.execute("DELETE FROM online_peers WHERE last_seen < ?", (now - 10,))
        cur = con.cursor()
        cur.execute("SELECT peer_id, username FROM online_peers")
        return jsonify([{"peer_id": r[0], "username": r[1]} for r in cur.fetchall()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['u']
        session["user_id"], session["username"] = u, u
        return redirect('/')
    return '<body style="background:#0f1216;color:white;text-align:center;padding-top:100px;"><form method="post"><h2>Giriş</h2><input name="u" placeholder="Adınız" required style="padding:10px;"><br><br><button style="padding:10px 20px;">Giriş Yap</button></form></body>'

@app.route('/logout')
def logout():
    if "username" in session:
        with sqlite3.connect(DB) as con:
            con.execute("DELETE FROM online_peers WHERE username=?", (session["username"],))
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
