from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Aktif kullanıcıları saklamak için
users = {}

@app.route('/')
def index():
    # templates/index.html dosyasını arar
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data.get('username', 'Misafir')
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
    # Görüntü sinyallerini karşı tarafa iletir
    emit('signal', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
