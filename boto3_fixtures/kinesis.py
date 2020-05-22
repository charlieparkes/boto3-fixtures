"""
Example Usage

```python
@pytest.fixture(scope="session")
def kinesis_streams():
    return ["TEST_KINESIS_STREAM"]

@pytest.fixture(scope="class")
def kinesis(localstack, kinesis_streams):
    with boto3_fixtures.setup(kinesis_streams) as streams:
        yield streams
```
"""


import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_stream(name: str, waiter_config: dict = {"Delay": 2, "MaxAttempts": 2}):
    client = boto3_fixtures.contrib.boto3.client("kinesis")
    resp = utils.call(client.create_stream, StreamName=name, ShardCount=1)
    client.get_waiter("stream_exists").wait(StreamName=name, WaiterConfig=waiter_config)
    return resp


def create_streams(names: list):
    return {n: create_stream(n) for n in names}


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_stream(name: str, waiter_config: dict = {"Delay": 2, "MaxAttempts": 2}):
    client = boto3_fixtures.contrib.boto3.client("kinesis")
    resp = utils.call(client.delete_stream, StreamName=name)
    client.get_waiter("stream_not_exists").wait(
        StreamName=name, WaiterConfig=waiter_config
    )
    return resp


def destroy_streams(names: list):
    return {n: destroy_stream(n) for n in names}


def setup(names):
    names = create_streams(names)
    return {"names": names}


def teardown(names):
    destroy_streams(names)
