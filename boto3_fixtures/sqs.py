"""
Example Usage

```python
@pytest.fixture(scope="session")
def sqs_queues():
    return ["TEST_SQS_QUEUE"]

@pytest.fixture(scope="class")
def sqs(localstack, sqs_queues):
    with boto3_fixtures.setup_s3(s3_buckets) as buckets:
        yield buckets
```
"""

import json

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils
from boto3_fixtures.contrib.sqs import get_queue_arn
from boto3_fixtures.utils import backoff_check


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_queue(q, dlq_url=None):
    client = boto3_fixtures.contrib.boto3.client("sqs")
    attrs = {}
    if dlq_url:
        attrs["RedrivePolicy"] = json.dumps(
            {"deadLetterTargetArn": get_queue_arn(dlq_url), "maxReceiveCount": 1}
        )
    resp = utils.call(client.create_queue, QueueName=q, Attributes=attrs)
    utils.call(
        backoff_check,
        func=lambda: boto3_fixtures.contrib.boto3.client("sqs").get_queue_url(
            QueueName=q
        ),
    )
    return resp["QueueUrl"]


def create_queues(names: list, redrive=False):
    resp = {}
    for n in names:
        if redrive:
            dlq_name = f"{n}-dlq"
            resp[dlq_name] = create_queue(dlq_name)
            resp[n] = create_queue(n, dlq_url=resp[dlq_name])
        else:
            resp[n] = create_queue(n)

    return resp


@backoff.on_exception(backoff.expo, ClientError, max_tries=3)
def destroy_queue(url):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("sqs").delete_queue, QueueUrl=url
    )


def destroy_queues(queues: dict):
    return {name: destroy_queue(url) for name, url in queues.items()}


def setup(names: list, redrive=False):
    queues = create_queues(names, redrive=redrive)
    return {"queues": queues}


def teardown(queues):
    return destroy_queues(queues)
