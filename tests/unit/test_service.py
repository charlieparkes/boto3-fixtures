import pytest

import boto3_fixtures


def test_unsupported_service():
    with pytest.raises(boto3_fixtures.exceptions.UnsupportedServiceException):
        boto3_fixtures.Service("foobar")
