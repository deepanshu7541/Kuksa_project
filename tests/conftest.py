import os
import pytest
from kuksa_client.grpc import VSSClient

HOST = os.getenv("DATABROKER_HOST", "127.0.0.1")
PORT = int(os.getenv("DATABROKER_PORT", "55556"))

@pytest.fixture(scope="module")
def client():
    c = VSSClient(HOST, PORT)
    c.connect()
    yield c
