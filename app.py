import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_users = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('find_match')
def handle_find_match():
    global waiting_users
    if len(waiting_users) > 0:
        partner_sid = waiting_users.pop(0)
        room = f"room_{partner_sid}"
        join_room(room)
        emit('match_found', {'room': room, 'init': True})
        emit('match_found', {'room': room, 'init': False}, room=partner_sid)
    else:
        waiting_users.append(request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
