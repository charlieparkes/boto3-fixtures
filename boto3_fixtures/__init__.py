"""
boto3-fixtures
~~~~~~~~~

Simple test fixtures for your local AWS cloud stack of choice
"""

# flake8: noqa

from boto3_fixtures._version import __version__

from .awslambda import *
from .dynamodb import *
from .kinesis import *
from .s3 import *
from .sqs import *
from .utils import *
