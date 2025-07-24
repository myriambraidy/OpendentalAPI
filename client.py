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

def get_procnotes():
    import requests
    url = 'http://localhost:30222/api/v1/procnotes'
    headers = {
        'Authorization': 'ODFHIR NFF6i0KrXrxDkZHt/VzkmZEaUWOjnQX2z'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        print('[CLIENT] OpenDental procnotes:', resp.json())
    except requests.RequestException as e:
        print('[CLIENT] Error fetching procnotes:', e, getattr(e.response, 'text', None))

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

if __name__ == '__main__':
    input("Press Enter to fetch procnotes...")
    get_procnotes()
    sio.wait()
