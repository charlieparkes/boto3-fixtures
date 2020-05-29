from contextlib import ExitStack
from typing import List

import boto3_fixtures as b3f
from boto3_fixtures.exceptions import UnsupportedServiceException

try:
    import pytest
except ImportError:
    raise Exception("This module requires pytest.")


def service_fixture(service: str, scope="function", autouse=False, **kwargs):
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
        with b3f.Service(service, **kwargs) as state:
            yield state

    return _fixture


def moto_fixture(
    services: List[str],
    region_name="us-east-1",
    scope="function",
    autouse=False,
    **kwargs
):
    try:
        import moto
    except ImportError as e:
        raise Exception("You must install moto to use this fixture.") from e

    MOCKS = {
        "sqs": moto.mock_sqs,
        "dynamodb": moto.mock_dynamodb2,
        "kinesis": moto.mock_kinesis,
        "s3": moto.mock_s3,
        "lambda": moto.mock_lambda,
    }

    ENV = {
        "AWS_DEFAULT_REGION": region_name,
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing",
    }

    try:
        managers = [MOCKS[s.lower()] for s in services]
    except KeyError as e:
        raise UnsupportedServiceException("Service unsupported.") from e

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture():
        with ExitStack() as stack:
            stack.enter_context(b3f.utils.set_env(ENV))
            for mgr in managers:
                stack.enter_context(mgr())
            yield

    return _fixture
