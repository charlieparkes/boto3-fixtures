# boto3-fixtures
[![PyPI version](https://img.shields.io/pypi/v/boto3-fixtures.svg)](https://pypi.org/project/boto3-fixtures/) [![TravisCI build status](https://travis-ci.com/alphachai/boto3-fixtures.svg?branch=master)](https://travis-ci.com/github/alphachai/boto3-fixtures) [![Code Coverage](https://img.shields.io/codecov/c/github/alphachai/boto3-fixtures.svg)](https://codecov.io/gh/alphachai/boto3-fixtures)

**boto3-fixtures** provides test fixtures for your local AWS cloud stack.

Testing software which touches cloud infrastructure doesn't have to be difficult! `boto3-fixtures` provides a dead-simple framework for setup+teardown of mocked AWS infrastructure. Use in combination with projects like moto or localstack.

### Supports
* Kinesis
* SQS
* S3
* Lambda
* DynamoDB

*Please submit a PR or issue if you'd like to see support for a specific AWS service!*


## Getting Started

This library provides a context decorator, `boto3_fixtures.Service`, which will setup and teardown AWS services.

```python
import boto3_fixtures

with boto3_fixtures.Service("sqs", queues=["my-queue"]) as svc:
    # Queues exist
    for queue in svc.state["queues"]:
      print(f"{queue.name} - {queue.arn} - {queue.url}")

# Queues destroyed
```

Combine this with a local testing stack of your choice (moto, localstack).

```python
import boto3_fixtures, moto

with moto.mock_sqs():
    with boto3_fixtures.Service("sqs", queues=["first-queue", "second-queue"]) as svc:
      # ...
```

### Generating Pytest Fixtures

To make your life even easier, we've boiled all of the above down into pytest fixture generators.

```python
import boto3_fixtures as b3f

aws = b3f.contrib.pytest.moto_fixture(
  services=["dynamodb", "kinesis", "sqs", "s3", "lambda"],
  scope="class",
)

sqs = b3f.contrib.pytest.service_fixture("sqs", scope="class", queues=fixtures.SQS)
kinesis = b3f.contrib.pytest.service_fixture("kinesis", scope="class", streams=fixtures.KINESIS)
dynamodb = b3f.contrib.pytest.service_fixture("dynamodb", scope="class", tables=fixtures.DYNAMODB)
s3 = b3f.contrib.pytest.service_fixture("s3", scope="class", buckets=fixtures.S3)
lam = b3f.contrib.pytest.service_fixture("lambda", scope="class", lambdas=fixtures.LAMBDA)
sns = b3f.contrib.pytest.service_fixture("sns", scope="class", topics=fixtures.TOPICS)


# Example Usage
def test_my_code(sqs):
    boto3.client("sqs").list_queues()
```

#### The `aws()` fixture

To ensure your mocked cloud is a dependency of your service fixtures, boto3-fixtures expects you to create a fixture named `aws`. If you don't take advantage of this, your local cloud stack may be torn down before your service, leading to boto3 exceptions when tearing down the services.

```python
# Example: localstack via pytest-localstack
import pytest_localstack

aws = pytest_localstack.patch_fixture(
  services=["sqs"],
  scope="class",
)

# Example: moto via boto3-fixtures
import boto3_fixtures as b3f

aws = b3f.contrib.pytest.moto_fixture(
  services=["sqs"],
  scope="class",
)
```

### Configuring Services

Configuration of a service may be either a list of *names* `List[str]` or a list of *configs* `List[dict]` containing boto3 parameters.

| Service  | List of Names | List of Configs |
| -------- | ------------- | --------------- |
| s3       | yes           | yes             |
| sqs      | yes           | yes             |
| kinesis  | yes           | yes             |
| dynamodb |               | yes             |
| lambda   |               | yes             |
| sns      | yes           | yes             |

For example, your configuration might look like this:

```python
S3 = ["first-bucket", "second-bucket"]

SQS = ["first-queue", "second-queue"]

KINESIS = ["first-stream", "second-stream"]

DYNAMODB = [
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

LAMBDA = [
    {
        "zip_path": "dist/build.zip",
        "FunctionName": "my_lambda",
        "Runtime": "python3.6",
        "Environment": {"foo": True},
    }
]

SNS = [
    "my-topic-with-default-attrs",
    {
        "Name": "my-topic-with-additional-params",
        "Tags": [{"Key": "key1", "Value": "val1"}],
        "Attributes": {
            "DisplayName": "YourSystemIsOnFireTopic",
        },
    }
]
```

These configurations don't have to be static. You could use a pytest fixture to build or compile a list of resources that you want mocked.

### Using both `moto` and `localstack`

You can point the `aws` fixture at moto or localstack to explicitly to require a specific stack to exist for the duration of your service fixture. For example, if you use both stacks:

```python
# conftest.py
stack_config = {
    "services": ["dynamodb", "kinesis", "sqs", "s3", "lambda"],
    "scope": "class",
    "autouse": False,
    "region_name": "us-east-1",
}

localstack = pytest_localstack.patch_fixture(**stack_config)
moto = b3f.contrib.pytest.moto_fixture(**stack_config)

@pytest.fixture(scope="class")
def aws(moto):
    pass

# component/conftest.py
@pytest.fixture(scope="class")
def aws(localstack):
    pass
```

## Known Issues

* Using both pytest-localstack and moto in the same project may break if the pytest-localstack tests run first. It's suspected this is due to an issue with cleanup with the pytest-localstack session, but is this is still under investigation.
