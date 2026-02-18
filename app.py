import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
def handle_global_msg(data):
    emit('receive_msg', {'sender': users[request.sid], 'message': data['message'], 'type': 'global'}, broadcast=True)

# GÖRÜNTÜ SİNYAL TAŞIYICI (KRİTİK KISIM)
@socketio.on('signal')
def handle_signal(data):
    target_sid = next((sid for sid, name in users.items() if name == data['target']), None)
    if target_sid:
        emit('signal', {'sender': users[request.sid], 'data': data['data']}, room=target_sid)

@socketio.on('send_private_event')
def handle_private_event(data):
    target_sid = next((sid for sid, name in users.items() if name == data['target']), None)
    if target_sid:
        emit('receive_msg', {'sender': users[request.sid], 'message': data.get('message', ''), 'type': data['type']}, room=target_sid)
        if data['type'] == 'private':
            emit('receive_msg', {'sender': 'Sen', 'message': data['message'], 'type': 'private'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
