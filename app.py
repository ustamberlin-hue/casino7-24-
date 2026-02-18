import os
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'casino724_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Aktif kullanıcıları takip et
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register')
def handle_register(username):
    users[request.sid] = username
    emit('update_user_list', list(users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        del users[request.sid]
        emit('update_user_list', list(users.values()), broadcast=True)

@socketio.on('send_global_msg')
def handle_global(data):
    # Herkese açık mesaj
    emit('receive_msg', {'sender': users[request.sid], 'msg': data['msg'], 'type': 'global'}, broadcast=True)

@socketio.on('send_private_msg')
def handle_private(data):
    # Özel mesaj (sadece hedef kişiye)
    target_sid = next((sid for sid, name in users.items() if name == data['target']), None)
    if target_sid:
        emit('receive_msg', {'sender': users[request.sid], 'msg': data['msg'], 'type': 'private'}, room=target_sid)
        emit('receive_msg', {'sender': 'Sen', 'msg': data['msg'], 'type': 'private'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
