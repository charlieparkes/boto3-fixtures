import logging

# import moto
import pytest
import pytest_localstack
from tests import fixtures

import boto3_fixtures as b3f

logger = logging.getLogger()

stack_config = {
    "services": ["dynamodb", "kinesis", "sqs", "s3", "lambda", "sns"],
    "scope": "class",
    "autouse": False,
    "region_name": fixtures.ENV["AWS_DEFAULT_REGION"],
}

localstack = pytest_localstack.patch_fixture(**stack_config)
moto = b3f.contrib.pytest.moto_fixture(**stack_config)

sqs = b3f.contrib.pytest.service_fixture("sqs", scope="class", queues=fixtures.SQS)
kinesis = b3f.contrib.pytest.service_fixture(
    "kinesis", scope="class", streams=fixtures.KINESIS,
)
dynamodb = b3f.contrib.pytest.service_fixture(
    "dynamodb", scope="class", tables=fixtures.DYNAMODB,
)
s3 = b3f.contrib.pytest.service_fixture("s3", scope="class", buckets=fixtures.S3)
lam = b3f.contrib.pytest.service_fixture(
    "lambda", scope="class", lambdas=fixtures.LAMBDA,
)
sns = b3f.contrib.pytest.service_fixture("sns", scope="class", topics=fixtures.SNS)


@pytest.fixture(scope="class")
def aws(moto):
    pass


def _string_or_key(v, key):
    if isinstance(v, str):
        return v
    return v[key]


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
    return [_string_or_key(q, "QueueName") for q in fixtures.SQS]


@pytest.fixture(scope="session")
def dynamodb_tables():
    return [t["TableName"] for t in fixtures.DYNAMODB]


@pytest.fixture(scope="session")
def sns_topics():
    return [_string_or_key(tpc, "Name") for tpc in fixtures.SNS]


@pytest.fixture(scope="session")
def s3_buckets():
    return fixtures.S3


@pytest.fixture(scope="class")
def environment(sqs_queues, kinesis_streams, dynamodb_tables, s3_buckets, sns_topics):
    # Ideally, nothing should have to "spin up" to run this fixture (for example, localstack)
    return b3f.utils.environment(
        fixtures=fixtures.ENV,
        sqs_queues=sqs_queues,
        kinesis_streams=kinesis_streams,
        dynamodb_tables=dynamodb_tables,
        s3_buckets=s3_buckets,
        sns_topics=sns_topics,
    )


@pytest.fixture(scope="function")
def set_environment(environment):
    with b3f.utils.set_env(environment()):
        yield


@pytest.fixture(scope="session")
def lambda_functions():
    return fixtures.LAMBDA
