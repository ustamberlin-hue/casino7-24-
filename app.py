import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# {sid: username}
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

# GENEL SOHBET
@socketio.on('send_global_msg')
def handle_global_msg(data):
    emit('receive_msg', {'sender': users[request.sid], 'message': data['message'], 'type': 'global'}, broadcast=True)

# ÖZEL SOHBET VE ARAMA İSTEĞİ
@socketio.on('send_private_event')
def handle_private_event(data):
    # data: {'target': 'isim', 'message': '...', 'type': 'private/call_req/call_cancel'}
    target_sid = next((sid for sid, name in users.items() if name == data['target']), None)
    if target_sid:
        emit('receive_msg', {'sender': users[request.sid], 'message': data.get('message', ''), 'type': data['type']}, room=target_sid)
        if data['type'] == 'private':
            emit('receive_msg', {'sender': 'Sen', 'message': data['message'], 'type': 'private'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
