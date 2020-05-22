"""
Example Usage:

```python
@pytest.fixture(scope="class")
def s3(localstack, s3_buckets):
    with boto3_fixtures.setup_s3(s3_buckets) as buckets:
        yield buckets
```
"""


import backoff
from botocore.exceptions import ClientError, ConnectionClosedError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def create_bucket(b: str):
    client = boto3_fixtures.contrib.boto3.client("s3")
    resp = utils.call(client.create_bucket, Bucket=b)
    client.get_waiter("bucket_exists").wait(Bucket=b)
    return resp


def create_buckets(names: list):
    return {n: create_bucket(n) for n in names}


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def destroy_bucket(b: str):
    client = boto3_fixtures.contrib.boto3.client("s3")
    objects = boto3_fixtures.contrib.boto3.resource("s3").Bucket(b).objects.all()
    [utils.call(client.delete_object, Bucket=b, Key=o.key) for o in objects]
    resp = utils.call(client.delete_bucket, Bucket=b)
    client.get_waiter("bucket_not_exists").wait(Bucket=b)
    return resp


def destroy_buckets(names: list):
    return {n: destroy_bucket(n) for n in names}


def setup(names):
    create_buckets(names)
    return {"names": names}


def teardown(names):
    destroy_buckets(names)
