import pytest
import socket

from conftest import ConnectionClass


@pytest.mark.usefixtures("start_tcp_server")
class TestServer:
    con = ConnectionClass()
    MAX_BYTES = 1024

    def test_send_message(self):
        MSG = "Nothing really important\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.client_address)
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            assert data is not None

    def test_echo(self):
        MSG = "Hello, world\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.client_address)
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            data = str(data.decode("utf-8"))
            assert data == MSG

    @pytest.mark.skip("Feature is not implemented")
    def test_shutdown(self):
        pass
