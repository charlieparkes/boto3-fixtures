try:
    import pytest
except ImportError:
    raise Exception("boto3_fixtures.contrib.pytest requires the pytest package")


@pytest.fixture
def boto3_fixture():
    pass
