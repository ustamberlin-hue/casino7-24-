from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Aktif kullanıcıları saklamak için sözlük
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    users[request.sid] = username
    join_room('chat_room')
    # Yeni listeyi herkese gönder
    emit('user_list', list(users.values()), room='chat_room')
    print(f"{username} katıldı.")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        # Güncel listeyi herkese gönder (çıkan kişi silinmiş olur)
        emit('user_list', list(users.values()), room='chat_room')
        print(f"{username} ayrıldı.")

@socketio.on('signal')
def handle_signal(data):
    # Arama sinyallerini (offer, answer, candidate) hedefe ilet
    emit('signal', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
