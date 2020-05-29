from collections import namedtuple
from typing import Dict, List, Union

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils

KinesisStream = namedtuple("Stream", ["name", "response"])


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_stream(StreamName: str, ShardCount: int, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("kinesis")
    resp = utils.call(
        client.create_stream, StreamName=StreamName, ShardCount=ShardCount, **kwargs
    )
    client.get_waiter("stream_exists").wait(
        StreamName=StreamName, WaiterConfig={"Delay": 2, "MaxAttempts": 2}
    )
    return KinesisStream(name=StreamName, response=resp)


def create_streams(streams: List[dict]):
    return {s.name: s for s in [create_stream(**stream) for stream in streams]}


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_stream(StreamName: str, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("kinesis")
    resp = utils.call(client.delete_stream, StreamName=StreamName)
    client.get_waiter("stream_not_exists").wait(
        StreamName=StreamName, WaiterConfig={"Delay": 2, "MaxAttempts": 2}
    )
    return resp


def destroy_streams(streams: Dict[str, KinesisStream]):
    return [destroy_stream(s.name) for _, s in streams.items()]


def setup(streams: Union[List[str], List[dict]], **kwargs):
    if isinstance(streams, list):
        streams = [{"StreamName": name, "ShardCount": 1, **kwargs} for name in streams]
    return {"streams": create_streams(streams)}


def teardown(streams):
    destroy_streams(streams)
