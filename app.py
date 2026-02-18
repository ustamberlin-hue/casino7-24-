from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data.get('username', 'Bilinmeyen')
    users[request.sid] = username
    join_room('chat_room')
    emit('user_list', list(users.values()), room='chat_room')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        del users[request.sid]
        emit('user_list', list(users.values()), room='chat_room')

@socketio.on('signal')
def handle_signal(data):
    # Sinyalin içine 'arayan kişi' bilgisini ekleyip öyle gönderiyoruz
    if request.sid in users:
        data['sender_name'] = users[request.sid]
    data['sender_id'] = request.sid
    emit('signal', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
