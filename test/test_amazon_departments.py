import os
import unittest

import requests

unittest.TestLoader.sortTestMethodsUsing = None


class TestBSR(unittest.TestCase):
    bsr_id: str | None = None

    def test_departments_bsr(self):
        res = requests.post(
            'http://0.0.0.0:' + str(os.environ.get('BSR_PORT', 8839)) + '/v1/bsr/load/bsr',
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'departments_flat_tree': {
                    'Test Top level': '/bestsellers/primary',
                    'Second level': '/bestsellers/secondary',
                },
            },
        )
        assert res.status_code == 200, 'Status code is not 200: ' + str(res.status_code)
        data = res.json()
        assert 'bsr_id' in data, 'Invalid result data!'
        self.bsr_id = data['bsr_id']
        print('BSR ID:', self.bsr_id)

    def test_departments_asins(self):
        res = requests.post(
            'http://0.0.0.0:' + str(os.environ.get('BSR_PORT', 8839)) + '/v1/bsr/load/asins',
            json={},
        )
        assert res.status_code == 200, 'Status code is not 200: ' + str(res.status_code)
