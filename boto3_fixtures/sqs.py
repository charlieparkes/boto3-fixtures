import json
from collections import namedtuple
from typing import Dict, List, Union

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils
from boto3_fixtures.contrib import mindictive as mdict
from boto3_fixtures.contrib.sqs import get_queue_arn
from boto3_fixtures.utils import backoff_check

SQSQueue = namedtuple("Queue", ["name", "url", "arn", "response"])


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_queue(QueueName, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("sqs")
    resp = utils.call(client.create_queue, QueueName=QueueName, **kwargs)
    utils.call(
        backoff_check,
        func=lambda: boto3_fixtures.contrib.boto3.client("sqs").get_queue_url(
            QueueName=QueueName
        ),
    )
    return SQSQueue(
        name=QueueName,
        url=resp["QueueUrl"],
        arn=get_queue_arn(resp["QueueUrl"]),
        response=resp,
    )


def create_queues(queues: List[dict]):
    return {q.name: q for q in [create_queue(**config) for config in queues]}


@backoff.on_exception(backoff.expo, ClientError, max_tries=3)
def destroy_queue(QueueUrl, **kwargs):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("sqs").delete_queue, QueueUrl=QueueUrl
    )


def destroy_queues(queues: Dict[str, SQSQueue]):
    return [destroy_queue(QueueUrl=q.url) for _, q in queues.items()]


def setup(queues: Union[List[str], List[dict]], **kwargs):
    queues = [
        {"QueueName": queue, **kwargs} if isinstance(queue, str) else queue
        for queue in queues
    ]

    def _dlq_name(queue_name):
        return f"{queue_name}-dlq"

    # Find queues that need a DLQ created by checking for RedrivePolicy=None
    redrive_key = ["Attributes", "RedrivePolicy"]

    # Create DLQs
    dlqs_to_create = [
        {"QueueName": _dlq_name(q["QueueName"])}
        for q in queues
        if isinstance(mdict.get_nested(q, redrive_key, None), dict)
    ]
    dlqs = create_queues(dlqs_to_create)

    # Update redrive policies with ARNs of DLQs
    defaults = {"maxReceiveCount": 1}
    policy = mdict.get_nested(kwargs, redrive_key, {})
    for q in queues:
        if isinstance(mdict.get_nested(q, redrive_key, None), dict):
            name = q["QueueName"]
            new_policy = {
                **defaults,
                **policy,
                "deadLetterTargetArn": dlqs[_dlq_name(name)].arn,
            }
            mdict.set_nested(
                q,
                redrive_key,
                json.dumps(new_policy),
            )
    return {"queues": create_queues(queues)}


def teardown(queues: Dict[str, SQSQueue], **kwargs):
    return destroy_queues(queues)
