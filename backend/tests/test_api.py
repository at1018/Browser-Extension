from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_user_me_endpoint():
    response = client.get('/api/users/me')
    assert response.status_code == 200
    assert response.json()['persona'] == 'developer'


def test_analyze_endpoint():
    payload = {
        'image_base64': 'data:image/png;base64,AAA',
        'source': 'test',
        'persona': 'student',
        'meta': {'context': 'unit test'},
    }
    response = client.post('/api/screenshots/analyze', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['persona'] == 'student'
    assert data['intent'] == 'unknown'
    assert 'analysis_id' in data


def test_screenshot_upload_endpoint():
    payload = {
        'source': 'test-upload',
        'user_id': 'test-user',
        'meta': {'source': 'unittest'},
    }
    response = client.post('/api/screenshots/upload', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'test-upload'
    assert data['status'] == 'uploaded'


def test_workflow_execute_endpoint():
    payload = {
        'workflow_id': 'demo-workflow',
        'screenshot_id': 'screenshot-1',
        'persona': 'qa',
        'input': {'task': 'generate tickets'},
    }
    response = client.post('/api/workflows/execute', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['workflow_id'] == 'demo-workflow'
    assert data['status'] == 'completed'
