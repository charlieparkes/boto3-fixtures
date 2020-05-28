import logging

# import moto
import pytest
import pytest_localstack
from tests import fixtures

import boto3_fixtures as b3f

logger = logging.getLogger()
services = ["dynamodb", "kinesis", "sqs", "s3", "lambda"]

localstack = pytest_localstack.patch_fixture(
    services=services,
    scope="class",
    autouse=False,
    region_name=fixtures.ENV["AWS_DEFAULT_REGION"],
)

moto = b3f.contrib.pytest.moto.generate_fixture(
    services=services,
    scope="class",
    autouse=False,
    region_name=fixtures.ENV["AWS_DEFAULT_REGION"],
)

sqs = b3f.contrib.pytest.generate_fixture("sqs", scope="class", queues=fixtures.SQS,)

kinesis = b3f.contrib.pytest.generate_fixture(
    "kinesis", scope="class", streams=fixtures.KINESIS,
)

dynamodb = b3f.contrib.pytest.generate_fixture(
    "dynamodb", scope="class", tables=fixtures.DYNAMODB,
)

s3 = b3f.contrib.pytest.generate_fixture("s3", scope="class", buckets=fixtures.S3)

lam = b3f.contrib.pytest.generate_fixture(
    "lambda", scope="class", lambdas=fixtures.LAMBDA,
)


@pytest.fixture(scope="session", autouse=True)
def requests_log_level():
    for name in ("requests", "urllib3"):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.propagate = True


@pytest.fixture(scope="session")
def kinesis_streams():
    return fixtures.KINESIS


@pytest.fixture(scope="session")
def sqs_queues():
    return fixtures.SQS


@pytest.fixture(scope="session")
def dynamodb_tables():
    return [t["TableName"] for t in fixtures.DYNAMODB]


@pytest.fixture(scope="session")
def s3_buckets():
    return fixtures.S3


@pytest.fixture(scope="class")
def environment(sqs_queues, kinesis_streams, dynamodb_tables, s3_buckets):
    # Ideally, nothing should have to "spin up" to run this fixture (for example, localstack)
    return b3f.utils.environment(
        fixtures=fixtures.ENV,
        sqs_queues=sqs_queues,
        kinesis_streams=kinesis_streams,
        dynamodb_tables=dynamodb_tables,
        s3_buckets=s3_buckets,
    )


@pytest.fixture(scope="function")
def set_environment(environment):
    with b3f.utils.set_env(environment()):
        yield


@pytest.fixture(scope="session")
def lambda_functions():
    return fixtures.LAMBDA


# @pytest.fixture(scope="class")
# def kinesis_localstack(localstack, kinesis_streams):
#     with b3f.Service("kinesis", streams=kinesis_streams) as streams:
#         yield streams


# @pytest.fixture(scope="class")
# def kinesis(kinesis_streams, environment, mock_aws):
#     with b3f.utils.set_env(environment()):
#         # with moto.mock_kinesis():
#         with b3f.Service("kinesis", streams=kinesis_streams) as streams:
#             yield streams


# @pytest.fixture(scope="class")
# def sqs_localstack(localstack, sqs_queues):
#     with b3f.Service("sqs", queues=sqs_queues) as queues:
#         yield queues


# @pytest.fixture(scope="class")
# def sqs(sqs_queues, environment, moto):
#     with b3f.utils.set_env(environment()):
#         # with moto.mock_sqs():
#         with b3f.Service("sqs", queues=fixtures.SQS) as queues:
#             yield queues


# @pytest.fixture(scope="class")
# def dynamodb_localstack(localstack, dynamodb_tables):
#     with b3f.Service("dynamodb", tables=fixtures.DYNAMODB) as tables:
#         yield tables


# @pytest.fixture(scope="class")
# def dynamodb(dynamodb_tables, environment, mock_aws):
#     with b3f.utils.set_env(environment()):
#         # with moto.mock_dynamodb2():
#         with b3f.Service("dynamodb", tables=fixtures.DYNAMODB) as tables:
#             yield tables


# @pytest.fixture(scope="class")
# def s3_localstack(localstack, s3_buckets):
#     with b3f.Service("s3", buckets=fixtures.S3) as buckets:
#         yield buckets


# @pytest.fixture(scope="class")
# def s3(s3_buckets, environment, mock_aws):
#     # with b3f.utils.set_env(environment()):
#     # with moto.mock_s3():
#     with b3f.Service("s3", buckets=fixtures.S3) as buckets:
#         yield buckets


# @pytest.fixture(scope="class")
# def lam_localstack(localstack, lambda_functions, environment):
#     for lam in lambda_functions:
#         lam["Environment"] = {**environment(), **lam.get("Environment", {})}
#
#     with b3f.Service("lambda", lambdas=lambda_functions):
#         yield


# @pytest.fixture(scope="class")
# def lam(lambda_functions, environment, mock_aws):
#     for lam in lambda_functions:
#         lam["Environment"] = {**environment(), **lam.get("Environment", {})}
#
#     # with b3f.utils.set_env(environment()):
#     # with moto.mock_lambda():
#     # [{**l, **{**environment(), **l.get("Environment", {})}} for l in fixtures.LAMBDA]
#     with b3f.Service("lambda", lambdas=lambda_functions):
#         yield
