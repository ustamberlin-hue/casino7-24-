import os
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neon_casino_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Kullanıcı verileri: {sid: {"name": "Ali", "role": "VIP", "active": True}}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register')
def handle_register(username):
    # İlk giren Admin olsun, sonrakiler Üye
    role = "Admin" if len(users) == 0 else "Üye"
    users[request.sid] = {"name": username, "role": role}
    emit('update_users', list(users.values()), broadcast=True)

@socketio.on('send_msg')
def handle_msg(data):
    sender_info = users.get(request.sid)
    if not sender_info: return

    payload = {
        "sender": sender_info['name'],
        "role": sender_info['role'],
        "msg": data['msg'],
        "target": data['target']
    }

    if data['target'] == 'global':
        emit('receive_msg', payload, broadcast=True)
    else:
        # Özel mesaj: Sadece alıcıya ve gönderene
        for sid, info in users.items():
            if info['name'] == data['target'] or sid == request.sid:
                emit('receive_msg', payload, room=sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
