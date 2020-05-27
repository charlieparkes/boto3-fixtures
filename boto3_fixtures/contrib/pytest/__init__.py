import boto3

import boto3_fixtures

from . import moto

try:
    import pytest
except ImportError:
    raise Exception("boto3_fixtures.contrib.pytest requires the pytest package")


def generate_fixture(
    service_name: str,
    region_name="us-east-1",
    decorator=None,
    scope="function",
    autouse=False,
    **kwargs
):
    """Create a pytest fixture which will wrap setup/teardown of a service in a context manager.

    Args:
        scope (str, optional): The pytest scope which this fixture will use.
            Defaults to :const:`"function"`.
        autouse (bool, optional): If :obj:`True`, automatically use this
            fixture in applicable tests. Default: :obj:`False`
    Returns:
        A :func:`pytest fixture <_pytest.fixtures.fixture>`.

    """

    def _get_client():
        with boto3_fixtures.Service(service_name, **kwargs):
            yield boto3.client(service_name, region_name)

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture():
        with boto3_fixtures.utils.set_env(
            {"AWS_DEFAULT_REGION": region_name}, overwrite=False
        ):
            if decorator:
                with decorator():
                    yield _get_client()
            else:
                yield _get_client()

    return _fixture
