from contextlib import ExitStack
from typing import List

import boto3

import boto3_fixtures as b3f

try:
    import moto
    import pytest
except ImportError as e:
    raise Exception(
        "boto3_fixtures.contrib.pytest requires the packages moto and pytest"
    ) from e


def generate_fixture(
    services: List[str],
    region_name="us-east-1",
    scope="function",
    autouse=False,
    **kwargs
):
    MOCKS = {
        "sqs": moto.mock_sqs,
        "dynamodb": moto.mock_dynamodb2,
        "kinesis": moto.mock_kinesis,
        "s3": moto.mock_s3,
        "lambda": moto.mock_lambda,
    }

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture():
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
            raise Exception("Service unsupported.") from e
        with b3f.utils.set_env(ENV, overwrite=False):
            with ExitStack() as stack:
                for mgr in managers:
                    stack.enter_context(mgr())
                yield
            # managers = []
            # for mgr in [MOCKS[s.lower()] for s in services]:
            #     managers.append(mgr())
            #
            # [mgr.start() for mgr in managers]
            # yield
            # [mgr.stop() for mgr in managers]

    return _fixture
