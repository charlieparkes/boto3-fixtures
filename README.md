# boto3_fixtures
[![PyPI version](https://img.shields.io/pypi/v/boto3_fixtures.svg)](https://pypi.org/project/boto3_fixtures/) [![TravisCI build status](https://travis-ci.com/mintel/boto3_fixtures.svg?branch=master)](https://travis-ci.com/github/mintel/boto3_fixtures) [![Code Coverage](https://img.shields.io/codecov/c/github/mintel/boto3_fixtures.svg)](https://codecov.io/gh/mintel/boto3_fixtures)

**boto3_fixtures** provides test fixtures for your local AWS cloud stack of choice (such as moto or localstack).

The problem with testing cloud infrastructure is that you end up writing a whole framework of fixtures to setup and teardown resources during testing. This library solves solves that problem for AWS!
