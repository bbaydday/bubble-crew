from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
import eventlet

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['room'] = request.form['room']
        return redirect(url_for('chat'))
    return render_template('join.html')

@app.route('/chat')
def chat():
    if 'username' not in session or 'room' not in session:
        return redirect(url_for('join'))
    return render_template('chat.html', username=session['username'], room=session['room'])

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f"{username} has joined the room.", to=room)

@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = session.get('username', 'Anon')
    room = session.get('room')
    full_msg = f"{username}: {msg}"
    send(full_msg, to=room)

@socketio.on('disconnect')
def on_disconnect():
    username = session.get('username')
    room = session.get('room')
    if username and room:
        send(f"{username} left the room.", to=room)
        leave_room(room)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
