import json
import logging
from functools import wraps

import botocore
from decouple import config

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils
from boto3_fixtures.contrib import mindictive


def build(message_data, message_group_id=None):
    data = json.dumps(message_data, sort_keys=True)
    msg = {"Id": utils.hash(data), "MessageBody": data}
    if message_group_id:
        msg["MessageGroupId"] = str(message_group_id)
    return msg


def batch_put_messages(
    queue_url, messages, batch_size=10, message_group_id=None, **kwargs
):
    """Put messages into a sqs queue, batched by the maximum of 10."""
    assert batch_size <= 10  # send_message_batch will fail otherwise
    client = boto3_fixtures.contrib.boto3.client("sqs")
    responses = []
    for b in utils.batch(messages, batch_size):
        responses.append(
            utils.call(
                client.send_message_batch,
                QueueUrl=queue_url,
                Entries=[build(message, message_group_id) for message in b],
            )
        )
    return tuple(responses)


def put_message(queue_url, data, message_group_id=None, **kwargs):
    return batch_put_messages(
        queue_url=queue_url, messages=[data], message_group_id=message_group_id
    )


def get_queue_url(queue_name):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("sqs").get_queue_url, QueueName=queue_name
    )["QueueUrl"]


def get_queue_arn(queue_url):
    return mindictive.get_nested(
        utils.call(
            boto3_fixtures.contrib.boto3.client("sqs").get_queue_attributes,
            QueueUrl=queue_url,
            AttributeNames=["QueueArn"],
        ),
        ["Attributes", "QueueArn"],
    )


def delete_message_batch(queue_url, entries):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("sqs").delete_message_batch,
        QueueUrl=queue_url,
        Entries=entries,
    )
