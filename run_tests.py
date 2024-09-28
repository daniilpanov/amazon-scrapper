from fastapi.testclient import TestClient
import server_service as serv
from tests_ import *

client = TestClient(serv.app)


def test_h10():
    h10test.h10process(client)


def test_100asins():
    asins100test.find100asins_process(client)


def test_pt():
    pt_process(client)
