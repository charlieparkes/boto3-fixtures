import json
import logging
from functools import wraps

import botocore
from decouple import config

import boto3_fixtures.contrib.boto3
from boto3_fixtures.utils import batch, call, hash


def build(record_data):
    data = json.dumps(record_data, sort_keys=True)
    return {"Data": data, "PartitionKey": hash(data)}


def batch_put_records(stream_name, records, batch_size=500, **kwargs):
    """Put records into a kinesis stream, batched by the maximum of 500."""
    client = boto3_fixtures.contrib.boto3.client("kinesis")
    responses = []
    for b in batch(records, batch_size):
        responses.append(
            call(
                client.put_records,
                StreamName=stream_name,
                Records=[build(record) for record in b],
            )
        )
    return tuple(responses)


def put_record(stream_name, data, **kwargs):
    return batch_put_records(stream_name=stream_name, records=[data])
