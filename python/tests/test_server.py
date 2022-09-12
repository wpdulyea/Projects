import pytest
import socket

from conftest import ConnectionClass


def test_send_message():
    pass  # perform some webtest test for your app


@pytest.mark.usefixtures("start_tcp_server")
def test_echo():
    con = ConnectionClass()
    MAX_BYTES = 1024
    MSG = "Hello, world\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(con.client_address)
        client.sendall(bytes(MSG, "utf-8"))
        data = client.recv(MAX_BYTES)
        assert data is not None
        data = str(data.decode("utf-8"))
        assert data == MSG


def test_shutdown():
    pass


class TestClass:
    def test_method(self):
        pass
