from boto3_fixtures import utils
from boto3_fixtures.contrib import boto3, mindictive


def get_queue_url(queue_name):
    return utils.call(boto3.client("sqs").get_queue_url, QueueName=queue_name)[
        "QueueUrl"
    ]


def get_queue_arn(queue_url):
    return mindictive.get_nested(
        utils.call(
            boto3.client("sqs").get_queue_attributes,
            QueueUrl=queue_url,
            AttributeNames=["QueueArn"],
        ),
        ["Attributes", "QueueArn"],
    )
