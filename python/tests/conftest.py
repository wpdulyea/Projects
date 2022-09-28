import pytest
import os
import sys
import tempfile
from multiprocessing import Process

sys.path.append("../")
from servers.tcp_server import MPTCPServer, TCPMessageHandler

import algorithms.convertNum as convert

bind_address = "localhost"
port = 8080
server_address = (bind_address, port)


class ConnectionClass:
    server_address = (bind_address, port)
    client_address = server_address


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


@pytest.fixture(scope="session")
def start_tcp_server():
    server = MPTCPServer(server_address, TCPMessageHandler)
    worker = Process(target=server.serve_forever)
    worker.daemon = True
    worker.start()
    yield server

