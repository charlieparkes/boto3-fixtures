from collections import namedtuple
from typing import Dict, List

import backoff
import boto3
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
import boto3_fixtures.contrib.mindictive as mdict
from boto3_fixtures import utils

DynamoDBTable = namedtuple("Table", ["name", "arn", "response"])


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_table(TableName: str, **kwargs):
    kwargs.update({"BillingMode": "PAY_PER_REQUEST"})
    resp = utils.call(
        boto3.client("dynamodb").create_table, TableName=TableName, **kwargs
    )
    name = mdict.get_nested(resp, ["TableDescription", "TableName"])
    arn = mdict.get_nested(resp, ["TableDescription", "TableArn"])
    return DynamoDBTable(name=name, arn=arn, response=resp)


def create_tables(tables: list):
    client = boto3_fixtures.contrib.boto3.client("dynamodb")
    _tables = [create_table(**table) for table in tables]
    for table in _tables:
        client.get_waiter("table_exists").wait(
            TableName=table.name, WaiterConfig={"Delay": 1, "MaxAttempts": 30}
        )
        assert utils.call(client.describe_table, TableName=table.name)
    return {t.name: t for t in _tables}


@backoff.on_exception(backoff.expo, ClientError, max_tries=3)
def destroy_table(TableName: str, **kwargs):
    client = boto3_fixtures.contrib.boto3.client("dynamodb")
    return utils.call(client.delete_table, TableName=TableName)


def destroy_tables(tables: Dict[str, DynamoDBTable]):
    return [destroy_table(table.name) for _, table in tables.items()]


def setup(tables: List[dict]):
    return {"tables": create_tables(tables)}


def teardown(tables: Dict[str, DynamoDBTable], **kwargs):
    destroy_tables(tables)
