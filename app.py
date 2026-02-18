import os, sqlite3, time
from flask import Flask, request, redirect, session, render_template_string, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.secret_key = "kesin_cozum_v8"
socketio = SocketIO(app, cors_allowed_origins="*")
DB = "sohbet_v8.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS online_peers (peer_id TEXT PRIMARY KEY, username TEXT, last_seen REAL)")
init_db()

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Görüntülü Sohbet v8</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body { background: #0f1216; color: white; font-family: sans-serif; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 260px; background: #1a1e23; border-right: 1px solid #333; padding: 20px; }
        .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 15px; }
        video { width: 45%; max-width: 400px; background: #000; border-radius: 10px; transform: scaleX(-1); border: 1px solid #444; }
        #chat { width: 90%; height: 150px; background: #1a1e23; border: 1px solid #444; margin-top: 15px; overflow-y: auto; padding: 10px; border-radius: 5px; }
        .msg { margin-bottom: 5px; padding: 3px 8px; background: #2c323a; border-radius: 4px; font-size: 13px; }
        input { width: 70%; padding: 8px; border-radius: 5px; border: none; margin-top: 5px; }
        .user-card { background: #2c323a; padding: 8px; margin-bottom: 5px; border-radius: 5px; display: flex; justify-content: space-between; }
        #modal { display: none; position: fixed; top: 20%; left: 50%; transform: translateX(-50%); background: white; color: black; padding: 20px; border-radius: 10px; z-index: 99; }
    </style>
</head>
<body>
    <div id="modal">
        <h4 id="callerTitle">Arama Geliyor...</h4>
        <button onclick="acceptCall()" style="background:green; color:white;">Kabul Et</button>
        <button onclick="rejectCall()" style="background:red; color:white;">Reddet</button>
    </div>

    <div class="sidebar">
        <h3>Aktifler</h3>
        <div id="userList"></div>
    </div>

    <div class="main">
        <div id="status" style="color:yellow;">Sistem Hazır</div>
        <div style="display:flex; gap:10px; width:100%; justify-content:center;">
            <video id="localVideo" autoplay playsinline muted></video>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
        
        <button id="endBtn" onclick="endCall()" style="display:none; background:red; color:white; margin:10px; padding:10px;">📞 Aramayı Bitir</button>

        <div id="chat"></div>
        <div style="width:90%;">
            <input type="text" id="mInput" placeholder="Mesajınız...">
            <button onclick="sendMsg()" style="background:#3498db; color:white; padding:8px;">Gönder</button>
        </div>
    </div>

    <script>
        const socket = io();
        let myId, peer, currentCall, targetPeerId;
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');

        navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
            localVideo.srcObject = stream;
            peer = new Peer({
                config: {'iceServers': [{url: 'stun:stun.l.google.com:19302'}]}
            });

            peer.on('open', id => {
                myId = id;
                socket.emit('register', {id: id, user: "{{session['username']}}"});
            });

            peer.on('call', call => {
                currentCall = call;
                document.getElementById('modal').style.display = 'block';
            });
        });

        socket.on('new_msg', data => {
            const div = document.createElement('div');
            div.className = 'msg';
            div.innerHTML = `<b>${data.user}:</b> ${data.txt}`;
            document.getElementById('chat').appendChild(div);
        });

        socket.on('force_end', () => {
            if(currentCall) currentCall.close();
            remoteVideo.srcObject = null;
            document.getElementById('endBtn').style.display = 'none';
            document.getElementById('modal').style.display = 'none';
            document.getElementById('status').innerText = "Bağlantı Kesildi.";
        });

        function makeCall(pId) {
            targetPeerId = pId;
            currentCall = peer.call(pId, localVideo.srcObject);
            currentCall.on('stream', s => {
                remoteVideo.srcObject = s;
                document.getElementById('endBtn').style.display = 'block';
            });
        }

        function acceptCall() {
            document.getElementById('modal').style.display = 'none';
            currentCall.answer(localVideo.srcObject);
            currentCall.on('stream', s => {
                remoteVideo.srcObject = s;
                document.getElementById('endBtn').style.display = 'block';
            });
        }

        function endCall() {
            socket.emit('signal_end', {to: targetPeerId});
            if(currentCall) currentCall.close();
            remoteVideo.srcObject = null;
            document.getElementById('endBtn').style.display = 'none';
        }

        function rejectCall() {
            socket.emit('signal_end', {to: targetPeerId});
            document.getElementById('modal').style.display = 'none';
        }

        function sendMsg() {
            const txt = document.getElementById('mInput').value;
            socket.emit('send_msg', {txt: txt, user: "{{session['username']}}"});
            document.getElementById('mInput').value = "";
        }

        socket.on('update_users', users => {
            const list = document.getElementById('userList');
            list.innerHTML = "";
            users.forEach(u => {
                if(u.peer_id !== myId) {
                    list.innerHTML += `<div class="user-card">${u.username} <button onclick="makeCall('${u.peer_id}')">Ara</button></div>`;
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
    update_all()

@socketio.on('send_msg')
def handle_msg(data):
    emit('new_msg', data, broadcast=True)

@socketio.on('signal_end')
def handle_end(data):
    emit('force_end', room=data.get('to'), broadcast=True)

def update_all():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT peer_id, username FROM online_peers")
        users = [{"peer_id": r[0], "username": r[1]} for r in cur.fetchall()]
        emit('update_users', users, broadcast=True)

@app.route('/')
def index():
    if 'username' not in session: return redirect('/login')
    return render_template_string(UI_HTML)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['u']
        return redirect('/')
    return '<form method="post"><input name="u" placeholder="Adınız"><button>Gir</button></form>'

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
