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


## Getting Started

This library provides a context decorator, `boto3_fixtures.Service`, which will setup and teardown AWS services.

```python
from boto3_fixtures import Service

with Service("kinesis", ["my-kinesis-stream"]) as streams:
    # Streams exist

# Streams are destroyed
```

Combine this with a local testing stack of your choice (moto, localstack).

```python
import boto3, boto3_fixtures, moto

def test_my_code():
    with moto.mock_sqs():
        with boto3_fixtures.Service("sqs", names=["first-queue", "second-queue"]) as queues:
            client = boto3.client("sqs")
            response = client.list_queues()
            assert len(response["QueueUrls"]) == 2
```

You can create pytest fixtures to simplify this even further.

```python
import pytest, boto3_fixtures, moto

@pytest.fixture
def sqs_queues():
    return ["first-queue", "second-queue"]

@pytest.fixture
def sqs(sqs_queues):
    with moto.mock_sqs():
        with boto3_fixtures.Service("sqs", names=["first-queue", "second-queue"]) as queues:
            yield queues


@pytest.mark.usefixtures("sqs")
def test_my_code():
    # Queues exist for the duration of this test (or whatever scope you set on the fixture)
    pass
```


## WIP
* Tons more examples
* `pytest` plugin/fixtures
* More AWS services!

Please submit a PR or issue if you'd like to see support for a specific AWS service!
