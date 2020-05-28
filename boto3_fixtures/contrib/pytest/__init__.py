import boto3

import boto3_fixtures

from . import moto

try:
    import pytest
except ImportError:
    raise Exception("boto3_fixtures.contrib.pytest requires the pytest package")


def generate_fixture(
    service: str,
    region_name="us-east-1",
    scope="function",
    autouse=False,
    **kwargs
):
    """Create a pytest fixture which will wrap setup/teardown of a service.

    Args:
        scope (str, optional): The pytest scope which this fixture will use.
            Defaults to :const:`"function"`.
        autouse (bool, optional): If :obj:`True`, automatically use this
            fixture in applicable tests. Default: :obj:`False`
    Returns:
        A :func:`pytest fixture <_pytest.fixtures.fixture>`.

    """

    @pytest.fixture(scope=scope)
    def aws():
        pass

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture(request, aws):
        # with boto3_fixtures.utils.set_env({"AWS_DEFAULT_REGION": region_name}):
        with boto3_fixtures.Service(service, **kwargs) as state:
            yield state

    return _fixture
