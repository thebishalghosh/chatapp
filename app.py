from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devsecret')

# Config for PostgreSQL (to be set via environment variable for Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/chatdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    messages = db.relationship('Message', backref='user', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return redirect(url_for('chat'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password required')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('chat'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('chat.html')

@socketio.on('send_message')
def handle_send_message(data):
    user_id = session.get('user_id')
    username = session.get('username')
    content = data.get('content')
    if not user_id or not content:
        return
    message = Message(content=content, user_id=user_id)
    db.session.add(message)
    db.session.commit()
    emit('receive_message', {
        'username': username,
        'content': content,
        'timestamp': message.timestamp.isoformat()
    }, broadcast=True)

@socketio.on('fetch_messages')
def handle_fetch_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    emit('all_messages', [
        {
            'username': m.user.username,
            'content': m.content,
            'timestamp': m.timestamp.isoformat()
        } for m in messages
    ])

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True) 