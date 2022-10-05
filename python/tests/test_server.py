import pytest
import socket
from conftest import t_Connection


@pytest.mark.usefixtures("start_tcp_server")
class TestTCPServer():
    con = t_Connection()
    MAX_BYTES = 1024

    def test_send_message(self):
        MSG = "Nothing really important\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.tcp_addr())
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            assert data is not None

    def test_echo(self):
        MSG = "Hello, world\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.tcp_addr())
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            data = str(data.decode("utf-8"))
            assert data == MSG

    @pytest.mark.skip("Feature is not implemented")
    def test_delay(self):
        pass

    @pytest.mark.skip("Feature is not implemented")
    def test_shutdown(self):
        pass


@pytest.mark.usefixtures("start_serverfirst")
class TestServer:
    con = t_Connection()
    MAX_BYTES = 1024

    def test_connect(self):
        RSP = "RDY_TOECHO"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.srv_addr())
            data = client.recv(self.MAX_BYTES)
            data = str(data.decode("utf-8")).strip()
            assert data == RSP

    def test_send_message(self):
        MSG = "Nothing really important"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.srv_addr())
            ## Servers sends a rdy message, i.e. server response before client sends
            client.recv(self.MAX_BYTES)
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            assert data is not None

    def test_echo_message(self):
        MSG = "Hello, world\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.con.srv_addr())
            ## Servers sends a rdy message, i.e. server response before client sends
            client.recv(self.MAX_BYTES)
            client.sendall(bytes(MSG, "utf-8"))
            data = client.recv(self.MAX_BYTES)
            data = str(data.decode("utf-8"))
            assert data == MSG

    @pytest.mark.skip("Feature is not implemented")
    def test_shutdown(self):
        pass
