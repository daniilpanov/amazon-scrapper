import time
from starlette.testclient import TestClient


def find100asins_process(client: TestClient):
    response = client.post('/helium/get100asins', json={
        'alias': 'Test task (lipton tea)',
        'label': 'lipton',
        'type': 'tea',
    })
    assert response.status_code == 200, "Invalid status code received"
    ids = response.text
    print('100asins Task ID:', ids)
    assert len(ids.split('--')) == 2, "Invalid task ID received"
    result = None

    for _ in range(30):
        res = client.get('/helium/result_100asins/' + ids)
        if res.status_code == 200:
            result = res.json()
            break
        assert res.status_code == 204
        time.sleep(2)
    assert result is not None, "No result or very long process time error"
    assert result, "Empty result error"
    assert len(result) > 50, "So small result!"
