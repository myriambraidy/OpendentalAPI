import socketio
import requests
import jwt

# Get token from server
resp = requests.post('http://localhost:5000/login', json={'user': 'joe'})
token = resp.json()['token']
print(f"[CLIENT] Got token: {token}")

# Decode token to get username
payload = jwt.decode(token, options={"verify_signature": False})
username = payload.get('user')

sio = socketio.Client()

@sio.event
def connect():
    print(f'[CLIENT] Connected to server as {username}')

@sio.event
def message(data):
    print(f'[CLIENT] Received message (raw): {data}')

@sio.event
def disconnect():
    print('[CLIENT] Disconnected from server')

sio.connect(f'http://localhost:5000?token={token}')
sio.wait()
