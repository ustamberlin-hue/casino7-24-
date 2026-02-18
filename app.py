import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Aktif kullanıcıları sakla {sid: username}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Geçici bir isim ata
    users[request.sid] = f"User_{request.sid[:4]}"
    emit('update_user_list', list(users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        del users[request.sid]
        emit('update_user_list', list(users.values()), broadcast=True)

@socketio.on('send_private_msg')
def handle_private_msg(data):
    # data: {'target': 'kullanici_adi', 'message': 'merhaba'}
    target_sid = next((sid for sid, name in users.items() if name == data['target']), None)
    if target_sid:
        emit('receive_private_msg', {'sender': users[request.sid], 'message': data['message']}, room=target_sid)
        emit('receive_private_msg', {'sender': 'Sen', 'message': data['message']}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
