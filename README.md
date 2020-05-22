# boto3-fixtures
[![PyPI version](https://img.shields.io/pypi/v/boto3-fixtures.svg)](https://pypi.org/project/boto3-fixtures/) [![TravisCI build status](https://travis-ci.com/alphachai/boto3-fixtures.svg?branch=master)](https://travis-ci.com/github/alphachai/boto3-fixtures) [![Code Coverage](https://img.shields.io/codecov/c/github/alphachai/boto3-fixtures.svg)](https://codecov.io/gh/alphachai/boto3-fixtures)

**boto3-fixtures** provides test fixtures for your local AWS cloud stack.

Testing software which touches cloud infrastructure doesn't have to be difficult! `boto3-fixtures` provides a dead-simple framework for setup+teardown of mocked AWS infrastructure. Use in combination with projects like moto or localstack.

### Supports
* Kinesis
* SQS
* S3
* Lambda
* DynamoDB
