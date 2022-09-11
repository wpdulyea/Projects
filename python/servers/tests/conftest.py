try:
    import ssl
    from requests import session
    import pytest
except ImportError as err:
    print(f"Module import failed in {__name__} due to {err}")
    sys.exit(1)


def prepare_url(value):
    httpbin_url = value.url.rstrip("/") + "/"

    def inner(*suffix):
        return urljoin(httpbin_url, "/".join(suffix))

    return inner


@pytest.fixture
