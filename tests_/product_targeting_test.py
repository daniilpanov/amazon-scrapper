import time
import requests

from db_mongo import db


def pt_process():
    test_ref_asin = 'B0B5HN65QQ'
    response = requests.post('/product-targeting/start', json={
        'alias': 'Test task (B0B5HN65QQ)#Test-PT-Query',
        'reference': test_ref_asin,
        'limit': 100,
    })
    assert response.status_code == 200, "Invalid status code received"
    ids = response.text
    print('PT Task ID:', ids)
    assert len(ids.split('--')) == 2, "Invalid task ID received"

    for _ in range(60):
        res = requests.get('/product-targeting/result/' + ids)
        assert res.status_code == 200
        if int(res.text) == 1:
            break
        time.sleep(2)
    # count = db('amazon_data')['product_targeting'].count_documents({'reference': test_ref_asin})
    # assert count > 0, "No result or very long process time error"
