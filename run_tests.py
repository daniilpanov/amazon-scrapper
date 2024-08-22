from fastapi.testclient import TestClient
import server_service as serv
from tests_ import h10test


client = TestClient(serv.app)


def test_h10():
    h10test.h10process(client)
