import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'casino724secret'
app.config['SQLALCHEMY_DATABASE_DATA'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# VERİTABANI MODELLERİ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='Üye') # Admin, VIP, Üye
    is_active = db.Column(db.Boolean, default=False) # Admin onayı için

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

# Giriş ve Kayıt sistemini buraya ekleyeceğiz (Basit tutmak için index.html içine entegre edildi)

@socketio.on('send_global_msg')
def handle_global(data):
    emit('receive_msg', {'sender': data['user'], 'msg': data['msg'], 'type': 'global'}, broadcast=True)

@socketio.on('send_private_msg')
def handle_private(data):
    # data: {target: 'ali', msg: 'selam', sender: 'can'}
    emit('receive_msg', {'sender': data['sender'], 'msg': data['msg'], 'type': 'private'}, room=data['target'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
