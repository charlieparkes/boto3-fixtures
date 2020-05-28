"""
boto3-fixtures
~~~~~~~~~

Simple test fixtures for your local AWS cloud stack of choice
"""

# flake8: noqa

from collections import namedtuple
from contextlib import ContextDecorator
from enum import Enum

from boto3_fixtures import awslambda, contrib, dynamodb, kinesis, s3, sqs, utils
from boto3_fixtures._version import __version__

SERVICES = {
    "lambda": awslambda,
    "dynamodb": dynamodb,
    "kinesis": kinesis,
    "s3": s3,
    "sqs": sqs,
}


class Service(ContextDecorator):
    def __init__(self, service: str, *args, **kwargs):
        try:
            self.service = SERVICES[service.lower()]
            self.args = args
            self.kwargs = kwargs
            self.state = None
        except KeyError as e:
            raise Exception(f"Service '{service}' is not supported.") from e

    def __enter__(self):
        self.state = self.service.setup(*self.args, **self.kwargs)
        return self

    def __exit__(self, *exc):
        return self.service.teardown(**self.state)
