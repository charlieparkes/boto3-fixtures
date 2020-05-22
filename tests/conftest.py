import logging

import moto
import pytest
import pytest_localstack
from tests import fixtures

import boto3_fixtures as b3f

logger = logging.getLogger()
localstack = pytest_localstack.patch_fixture(
    services=["dynamodb", "kinesis", "sqs", "s3", "lambda"],
    scope="class",
    autouse=False,
    region_name=fixtures.ENV["AWS_DEFAULT_REGION"],
)


@pytest.fixture(scope="session", autouse=True)
def requests_log_level():
    for name in ("requests", "urllib3"):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.propagate = True


@pytest.fixture(scope="session")
def kinesis_streams():
    return ["test-kinesis-stream"]


@pytest.fixture(scope="class")
def kinesis_localstack(localstack, kinesis_streams):
    with b3f.kinesis.setup(kinesis_streams) as streams:
        yield streams


@pytest.fixture(scope="class")
def kinesis(kinesis_streams, environment):
    with b3f.utils.set_env(environment()):
        with moto.mock_kinesis():
            with b3f.kinesis.setup(kinesis_streams) as streams:
                yield streams


@pytest.fixture(scope="session")
def sqs_queues():
    return ["test-sqs-queue"]


@pytest.fixture(scope="class")
def sqs_localstack(localstack, sqs_queues):
    with b3f.sqs.setup(sqs_queues, redrive=True) as queues:
        yield queues


@pytest.fixture(scope="class")
def sqs(sqs_queues, environment):
    with b3f.utils.set_env(environment()):
        with moto.mock_sqs():
            with b3f.sqs.setup(sqs_queues, redrive=True) as queues:
                yield queues


@pytest.fixture(scope="session")
def dynamodb_tables():
    return [
        {
            "AttributeDefinitions": [
                {"AttributeName": "uri", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            "TableName": "test-dbd-table",
            "KeySchema": [
                {"AttributeName": "uri", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
        }
    ]


@pytest.fixture(scope="class")
def dynamodb_localstack(localstack, dynamodb_tables):
    with b3f.dynamodb.setup(dynamodb_tables) as tables:
        yield tables


@pytest.fixture(scope="class")
def dynamodb(dynamodb_tables, environment):
    with b3f.utils.set_env(environment()):
        with moto.mock_dynamodb2():
            with b3f.dynamodb.setup(dynamodb_tables) as tables:
                yield tables


@pytest.fixture(scope="session")
def s3_buckets():
    return ["test-bucket"]


@pytest.fixture(scope="class")
def s3_localstack(localstack, s3_buckets):
    with b3f.s3.setup(s3_buckets) as buckets:
        yield buckets


@pytest.fixture(scope="class")
def s3(s3_buckets, environment):
    with b3f.utils.set_env(environment()):
        with moto.mock_s3():
            with b3f.s3.setup(s3_buckets) as buckets:
                yield buckets


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
def lambdas():
    return [
        {
            "path": "dummy_lambda/dist/build.zip",
            "runtime": "python3.6",
            "environment": {"MOCK_AWS": True},
        }
    ]


@pytest.fixture(scope="class")
def lam_localstack(localstack, lambdas, environment):
    pass
    # with b3f.awslambda.setup(
    #     path="dummy_lambda/dist/build.zip",
    #     runtime="python3.6",
    #     environment=environment(MOCK_AWS=True),
    # ) as lam:
    #     yield lam
