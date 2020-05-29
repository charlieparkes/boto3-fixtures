from collections import namedtuple
from typing import Dict, List, Union

import backoff
from botocore.exceptions import ClientError, ConnectionClosedError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils

S3Bucket = namedtuple("Bucket", ["name", "response"])


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def create_bucket(Bucket: str, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("s3")
    resp = utils.call(client.create_bucket, Bucket=Bucket, **kwargs)
    client.get_waiter("bucket_exists").wait(Bucket=Bucket)
    return S3Bucket(name=Bucket, response=resp)


def create_buckets(buckets: List[dict]):
    return {b.name: b for b in [create_bucket(**bucket) for bucket in buckets]}


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def destroy_bucket(Bucket: str, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("s3")
    objects = boto3_fixtures.contrib.boto3.resource("s3").Bucket(Bucket).objects.all()
    [utils.call(client.delete_object, Bucket=Bucket, Key=o.key) for o in objects]
    resp = utils.call(client.delete_bucket, Bucket=Bucket)
    client.get_waiter("bucket_not_exists").wait(Bucket=Bucket)
    return resp


def destroy_buckets(buckets: Dict[str, S3Bucket]):
    return [destroy_bucket(b.name) for _, b in buckets.items()]


def setup(buckets: Union[List[str], List[dict]], **kwargs):
    if isinstance(buckets, list):
        buckets = [{"Bucket": name, **kwargs} for name in buckets]
    return {"buckets": create_buckets(buckets)}


def teardown(buckets: Dict[str, S3Bucket], **kwargs):
    destroy_buckets(buckets)
