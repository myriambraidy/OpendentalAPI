from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
import jwt
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='eventlet')

SECRET_KEY = 'your-secret-key'  # Change this!

# Map Socket.IO session IDs to user
connected_users = {}

@app.route('/hi')
def hi():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = payload.get('user', None)
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    if not user:
        return jsonify({'error': 'No user in token'}), 401
    # Find all session IDs for this user
    target_sids = [sid for sid, u in connected_users.items() if u == user]
    for sid in target_sids:
        print(f"[SERVER] Sending message to user '{user}' (sid: {sid}) via /hi")
        socketio.emit('message', {'data': f'Route /hi was hit by {user}!'}, room=sid)
    print(f"[SERVER] /hi triggered by user '{user}', sent to {len(target_sids)} session(s)")
    return f"Message sent to WebSocket clients for user {user}."

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        print('[SERVER] No token provided, disconnecting')
        disconnect()
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = payload.get('user', None)
        if not user:
            print('[SERVER] No user in token, disconnecting')
            disconnect()
            return
        connected_users[request.sid] = user
        print(f"[SERVER] WebSocket client connected as user: {user} (sid: {request.sid})")
    except jwt.InvalidTokenError:
        print('[SERVER] Invalid token, disconnecting')
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    user = connected_users.pop(request.sid, None)
    print(f"[SERVER] Client disconnected (user: {user}, sid: {request.sid})")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or {}
        user = data.get('user')
    else:
        user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Missing user'}), 400
    token = jwt.encode({'user': user}, SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000) 