from contextlib import ExitStack
from typing import List

import boto3

import boto3_fixtures as b3f

try:
    import moto
except ImportError:
    raise Exception("boto3_fixtures.contrib.pytest requires the moto package")
try:
    import pytest
except ImportError:
    raise Exception("boto3_fixtures.contrib.pytest requires the pytest package")


def generate_fixture(
    service_names: List[str],
    region_name="us-east-1",
    fixtures: list = [],
    scope="function",
    autouse=False,
    **kwargs
):
    MOCKS = {
        b3f.SERVICES.SQS: moto.mock_sqs,
        b3f.SERVICES.DYNAMODB: moto.mock_dynamodb2,
        b3f.SERVICES.KINESIS: moto.mock_kinesis,
        b3f.SERVICES.S3: moto.mock_s3,
        b3f.SERVICES.LAMBDA: moto.mock_lambda,
    }
    ENV = {
        "AWS_DEFAULT_REGION": region_name,
        # "AWS_ACCESS_KEY_ID": "moto",
        # "AWS_SECRET_ACCESS_KEY": "moto",
        # "AWS_SECURITY_TOKEN": "moto",
        # "AWS_SESSION_TOKEN": "moto",
    }

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture(*fixtures):
        with b3f.utils.set_env(ENV, overwrite=False):
            with ExitStack() as stack:
                for mgr in [MOCKS[s] for s in service_names]:
                    stack.enter_context(mgr())
                yield

    return _fixture
