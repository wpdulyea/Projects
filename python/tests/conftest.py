import pytest
import os
import tempfile

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
    print(f'Setting up your test run now..')

@pytest.fixture
def teardown():
    print(f'Cleaning up your test run now..')
   

