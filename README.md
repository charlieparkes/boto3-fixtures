# boto3-fixtures
[![PyPI version](https://img.shields.io/pypi/v/boto3-fixtures.svg)](https://pypi.org/project/boto3-fixtures/) [![TravisCI build status](https://travis-ci.com/alphachai/boto3-fixtures.svg?branch=master)](https://travis-ci.com/github/alphachai/boto3-fixtures) [![Code Coverage](https://img.shields.io/codecov/c/github/alphachai/boto3-fixtures.svg)](https://codecov.io/gh/alphachai/boto3-fixtures)

**boto3-fixtures** provides test fixtures for your local AWS cloud stack of choice (such as moto or localstack).

The problem with testing cloud infrastructure is that you end up writing a whole framework of fixtures to setup and teardown resources during testing. This library solves solves that problem for AWS!
