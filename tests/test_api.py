from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_upload_rejects_unsupported_extension():
    response = client.post('/api/upload', files=[('files', ('bad.exe', b'fake binary', 'application/octet-stream'))])
    assert response.status_code == 400
