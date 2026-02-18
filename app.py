import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neon_secret_724'
socketio = SocketIO(app, cors_allowed_origins="*")

# Kullanıcı Veritabanı Simülasyonu (Gerçek projede SQL kullanılır)
users = {} # {sid: {"username": "Ali", "role": "Üye", "active": False}}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('register')
def handle_register(data):
    # İsim çakışmasını önle
    username = data['username']
    if any(u['username'] == username for u in users.values()):
        emit('error', 'Bu isim zaten alınmış!')
        return
    
    users[request.sid] = {
        "username": username,
        "role": "Üye", # İlk kayıt olan 'Üye' olur, admin panelden değiştirilir
        "active": True
    }
    emit('update_list', list(users.values()), broadcast=True)

@socketio.on('send_msg')
def handle_msg(data):
    user_info = users.get(request.sid)
    if not user_info: return

    payload = {
        "sender": user_info['username'],
        "msg": data['msg'],
        "role": user_info['role'],
        "target": data['target']
    }

    if data['target'] == 'global':
        emit('receive_msg', payload, broadcast=True)
    else:
        # Özel Mesaj: Sadece gönderen ve alıcıya ilet
        target_sid = next((sid for sid, u in users.items() if u['username'] == data['target']), None)
        if target_sid:
            emit('receive_msg', payload, room=target_sid)
            emit('receive_msg', payload, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
