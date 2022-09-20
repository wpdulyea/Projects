import pytest
import os
import sys
import tempfile
from random import randrange
from multiprocessing import Process

sys.path.append("../")
from servers.tcp_server import MPTCPServer, TCPMessageHandler
from servers.serverfirst import MPServer, MessageHandler

bind_address = "localhost"
tcp_port = randrange(8080, 8180)
srv_port = randrange(8080, 8180)
server_address = (bind_address, srv_port)
tcp_address = (bind_address, tcp_port)

class ConnectionClass:
    def tcp_addr(self):
        return (bind_address, tcp_port)

    def srv_addr(self):
        return (bind_address, srv_port)


@pytest.fixture(scope="session")
def image_file(tmp_path_factory):
    img = compute_expensive_image()
    fn = tmp_path_factory.mktemp("data") / "img.png"
    img.save(fn)
    return fn


@pytest.fixture
def cleandir():
    with tempfile.TemporaryDirectory() as newpath:
        old_cwd = os.getcwd()
        os.chdir(newpath)
        yield
        os.chdir(old_cwd)


@pytest.fixture
def setup():
    print(f"Setting up your test run now..")


@pytest.fixture
def teardown():
    print(f"Cleaning up your test run now..")


@pytest.fixture(scope="class")
def start_tcp_server():
    server = MPTCPServer(tcp_address, TCPMessageHandler)
    worker = Process(target=server.serve_forever)
    worker.daemon = True
    worker.start()
    yield server
    #worker.join()


@pytest.fixture(scope="class")
def start_serverfirst():
    server = MPServer(server_address, MessageHandler)
    worker = Process(target=server.serve_forever)
    worker.daemon = True
    print(f"Host {server_address[0]} listening on port {server_address[1]}")
    print("Waiting to echo inbound messages")
    worker.start()
    yield server
    #worker.join()

