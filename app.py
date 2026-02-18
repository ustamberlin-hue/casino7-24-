import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "final_fix_2026"
# Mesajların ve komutların kesin gitmesi için SocketIO kullanıyoruz
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
DB = "sohbet_final.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, username TEXT, last_seen REAL)")
init_db()

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Görüntülü Sohbet & Mesaj v9</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 260px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; overflow-y: auto; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 15px; }
        .video-container { display: flex; gap: 10px; width: 100%; justify-content: center; }
        video { width: 45%; max-width: 400px; background: #000; border-radius: 10px; border: 1px solid #444; transform: scaleX(-1); }
        #chat { width: 90%; height: 200px; background: #1a1e23; border: 1px solid #444; margin-top: 15px; overflow-y: auto; padding: 10px; border-radius: 8px; }
        .msg { margin-bottom: 8px; padding: 5px; background: #2c323a; border-radius: 4px; font-size: 14px; border-left: 3px solid #3498db; }
        .user-card { background: #2c323a; padding: 10px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; }
        #modal { display: none; position: fixed; top: 25%; left: 50%; transform: translateX(-50%); background: white; color: black; padding: 25px; border-radius: 12px; z-index: 1000; box-shadow: 0 0 50px rgba(0,0,0,0.8); text-align:center; }
        button { cursor: pointer; border: none; border-radius: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <div id="modal">
        <h3 id="callerTitle">Arama Geliyor...</h3>
        <button onclick="acceptCall()" style="background:#2ecc71; color:white; padding:15px 30px; font-size:16px;">KABUL ET</button>
        <button onclick="rejectCall()" style="background:#e74c3c; color:white; padding:15px 30px; font-size:16px; margin-left:10px;">REDDET</button>
    </div>

    <div class="sidebar">
        <h3>Aktif Kişiler</h3>
        <div id="userList"></div>
    </div>

    <div class="main">
        <div id="status" style="color:#f1c40f; font-weight:bold; margin-bottom:10px;">Bağlanıyor...</div>
        <div class="video-container">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
        
        <button id="endBtn" onclick="endCall()" style="display:none; background:#e74c3c; color:white; margin:15px; padding:12px 30px; border-radius:8px;">📞 Aramayı Bitir / İptal Et</button>

        <div id="chat"></div>
        <div style="width:90%; display:flex; gap:10px; margin-top:10px;">
            <input type="text" id="mInput" placeholder="Mesaj yazın..." style="flex:1; padding:12px; border-radius:8px; border:none; background:#2c323a; color:white;">
            <button onclick="sendMsg()" style="background:#3498db; color:white; padding:0 25px;">GÖNDER</button>
        </div>
    </div>

    <script>
        const socket = io();
        let myId, peer, currentCall, activePartnerId;
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');

        navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
            localVideo.srcObject = stream;
            // Görüntü geçişini kolaylaştırmak için Google'ın STUN sunucularını ekledik
            peer = new Peer({ config: {'iceServers': [{url: 'stun:stun.l.google.com:19302'}, {url: 'stun:stun1.l.google.com:19302'}]} });

            peer.on('open', id => {
                myId = id;
                document.getElementById('status').innerText = "Çevrimiçi";
                socket.emit('register', {id: id, user: "{{session['username']}}"});
            });

            peer.on('call', call => {
                currentCall = call;
                document.getElementById('modal').style.display = 'block';
            });
        }).catch(e => alert("Kamera izni verilmedi!"));

        // MERKEZİ MESAJLAŞMA (SocketIO üzerinden - Kesin iletilir)
        function sendMsg() {
            const txt = document.getElementById('mInput').value;
            if(!txt) return;
            socket.emit('chat_msg', {txt: txt, user: "{{session['username']}}"});
            document.getElementById('mInput').value = "";
        }

        socket.on('receive_msg', data => {
            const div = document.createElement('div');
            div.className = 'msg';
            div.innerHTML = `<b>${data.user}:</b> ${data.txt}`;
            document.getElementById('chat').appendChild(div);
            document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
        });

        // MERKEZİ KAPATMA (Sinyal hatasını önler)
        socket.on('force_close', () => {
            if(currentCall) currentCall.close();
            remoteVideo.srcObject = null;
            document.getElementById('endBtn').style.display = 'none';
            document.getElementById('modal').style.display = 'none';
            document.getElementById('status').innerText = "Bağlantı Kesildi.";
        });

        function makeCall(pId) {
            activePartnerId = pId;
            currentCall = peer.call(pId, localVideo.srcObject);
            currentCall.on('stream', s => {
                remoteVideo.srcObject = s;
                document.getElementById('status').innerText = "Bağlantı Kuruldu!";
                document.getElementById('endBtn').style.display = 'block';
            });
        }

        function acceptCall() {
            document.getElementById('modal').style.display = 'none';
            currentCall.answer(localVideo.srcObject);
            currentCall.on('stream', s => {
                remoteVideo.srcObject = s;
                document.getElementById('endBtn').style.display = 'block';
                document.getElementById('status').innerText = "Görüntü Aktif";
            });
        }

        function endCall() {
            socket.emit('request_close'); // Herkese kapatma sinyali gönder
            if(currentCall) currentCall.close();
            remoteVideo.srcObject = null;
            document.getElementById('endBtn').style.display = 'none';
        }

        function rejectCall() {
            socket.emit('request_close');
            document.getElementById('modal').style.display = 'none';
        }

        socket.on('update_list', users => {
            const list = document.getElementById('userList');
            list.innerHTML = "";
            users.forEach(u => {
                if(u.peer_id !== myId) {
                    list.innerHTML += `<div class="user-card"><span>${u.username}</span> <button onclick="makeCall('${u.peer_id}')" style="background:#2ecc71; color:white;">ARA</button></div>`;
                }
            });
        });
    </script>
</body>
</html>
"""

@socketio.on('register')
def handle_reg(data):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT OR REPLACE INTO online_peers VALUES (?,?,?)", (data['id'], data['user'], time.time()))
    refresh_users()

@socketio.on('chat_msg')
def handle_chat(data):
    emit('receive_msg', data, broadcast=True)

@socketio.on('request_close')
def handle_close():
    emit('force_close', broadcast=True)

def refresh_users():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM online_peers WHERE last_seen < ?", (time.time() - 15,))
        cur.execute("SELECT peer_id, username FROM online_peers")
        users = [{"peer_id": r[0], "username": r[1]} for r in cur.fetchall()]
        emit('update_list', users, broadcast=True)

@app.route('/')
def index():
    if 'username' not in session: return redirect('/login')
    return render_template_string(UI_HTML)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['u']
        return redirect('/')
    return '<body style="background:#0f1216;color:white;text-align:center;padding-top:100px;"><form method="post"><h2>Giriş Yap</h2><input name="u" placeholder="Adınız" required style="padding:10px;"><br><br><button style="padding:10px 20px;">GİRİŞ</button></form></body>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
