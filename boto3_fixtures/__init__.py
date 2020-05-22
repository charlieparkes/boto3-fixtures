"""
boto3-fixtures
~~~~~~~~~

Simple test fixtures for your local AWS cloud stack of choice
"""

# flake8: noqa

from boto3_fixtures._version import __version__

from . import awslambda, dynamodb, kinesis, s3, sqs, utils
