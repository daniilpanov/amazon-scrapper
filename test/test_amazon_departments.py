import os
import unittest

import requests

unittest.TestLoader.sortTestMethodsUsing = None


class TestBSR(unittest.TestCase):
    bsr_id: str | None = None

    def test_all(self):
        self.t_departments_bsr()
        self.t_departments_asins()

    def test_all2(self):
        self.t_departments_bsr()
        self.t_departments_asins()

    def t_departments_bsr(self):
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
        assert res.status_code == 200, 'Status code is not 200: ' + str(res.status_code) + '[' + res.text + ']'
        data = res.json()
        assert 'bsr_id' in data, 'Invalid result data!'
        self.bsr_id = data['bsr_id']
        print('BSR ID:', self.bsr_id)

    def t_departments_asins(self):
        assert self.bsr_id, 'BSR ID is empty!'
        res = requests.post(
            'http://0.0.0.0:' + str(os.environ.get('BSR_PORT', 8839)) + '/v1/bsr/load/asins',
            json={
                'bsr_id': self.bsr_id,
                'asins': [
                    {'asin': 'test1', 'title': 'test1', 'image': 'ok!0', 'number_in_BSR': 1},
                    {'asin': 'test2', 'number_in_BSR': 2, 'title': 'test2', 'image': 'ok!'},
                    {'asin': 'test3', 'title': 'test3', 'image': 'ok!2'},
                    {'asin': 'test4', 'title': 'test4', 'image': 'ok!4', 'score': 5.1},
                    {'asin': 'test5', 'title': 'test5', 'image': 'ok!5', 'score': 2},
                    {'asin': 'test6'},
                ],
            },
        )
        assert res.status_code == 200, 'Status code is not 200: ' + str(res.status_code) + '[' + res.text + ']'
