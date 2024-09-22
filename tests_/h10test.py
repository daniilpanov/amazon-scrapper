import time

from fastapi.testclient import TestClient


def h10process(client: TestClient):
    response = client.post('/helium/get', json={
        'alias': 'Test task (B0D1CBVWYK, B001PMHUSW)',
        'asins': ['B0D1CBVWYK', 'B001PMHUSW'],
    })
    assert response.status_code == 200, "Invalid status code received"
    ids = response.text
    print('H10 Task ID:', ids)
    assert len(ids.split('--')) == 2, "Invalid task ID received"
    result = None

    for _ in range(30):
        res = client.get('/helium/result/' + ids)
        if res.status_code == 200:
            result = res.json()
            break
        assert res.status_code == 204
        time.sleep(1)
    if result:
        print('H10 Task Result Keys:', result.keys())
    else:
        print('H10 Task Result:', result)
    assert result is not None, "No result or very long process time error"
    assert result, "Empty result error"
    assert list(result.keys()) == ['amazon_data', 'helium_data'], "Some data keys lost"
    assert list(result['amazon_data'].keys()) == ['target', 'other'], "Some amazon data keys lost"
    assert list(result['amazon_data'].keys()) == ['target', 'other'], "Some amazon data keys lost"
    assert list(result['amazon_data']['target'].keys()) == ['title', 'description', 'brand'], \
        "Some amazon target data keys lost"
    assert list(result['amazon_data']['other'].keys()) == ['characteristics', 'about', 'variant', 'manufacturer', 'aplus'], \
        "Some amazon other data keys lost"
    assert list(result['helium_data'].keys()) == ['titles', 'image_urls', 'csv_data'], "Some helium data keys lost"
