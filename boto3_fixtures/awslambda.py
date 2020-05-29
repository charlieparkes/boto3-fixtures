"""
Example Usage

```python
@pytest.fixture(scope="class")
def lam(localstack, environment):
    with boto3_fixtures.setup(
                runtime="python3.6",
                environment=environment(MOCK_AWS=True),
            ) as lam:
        yield lam

@pytest.mark.usefixtures("lam")
def test():
    payload = [{...}, {...}]
    response, body = invoke(name="my_lambda", payload=sqs_payload(messages))
```
"""

import json
from collections import namedtuple
from pathlib import Path
from typing import Dict, List

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils

Lambda = namedtuple("Lambda", ["name", "response"])


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_lambda(
    FunctionName: str,
    Runtime: str,
    Role: str = "foobar",
    Handler: str = "main.handler",
    Environment: dict = {},
    Timeout: int = 300,
    zip_path: str = "dist/build.zip",
    **kwargs,
):
    def clean_env(env):
        for k, v in env.items():
            if isinstance(v, bool):
                if v:
                    env[k] = str(v)
                else:
                    continue
            elif isinstance(v, type(None)):
                env[k] = ""
        return env

    with open(str(Path().absolute() / zip_path), "rb") as f:
        resp = utils.call(
            boto3_fixtures.contrib.boto3.client("lambda").create_function,
            FunctionName=FunctionName,
            Runtime=Runtime,
            Role=Role,
            Handler=Handler,
            Code=dict(ZipFile=f.read()),
            Timeout=Timeout,
            Environment={"Variables": clean_env(Environment)},
            **kwargs,
        )
        return Lambda(name=FunctionName, response=resp)


def create_lambdas(lambdas):
    return {lam.name: lam for lam in [create_lambda(**lam) for lam in lambdas]}


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_lambda(FunctionName: str, **kwargs):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("lambda").delete_function,
        FunctionName=FunctionName,
    )


def destroy_lambdas(lambdas: Dict[str, Lambda]):
    return [destroy_lambda(l.name) for _, l in lambdas.items()]


def invoke(FunctionName: str, Payload: dict = {}, **kwargs):
    defaults = {
        "InvocationType": "RequestResponse",
        "LogType": "Tail",
        "Payload": json.dumps(Payload).encode(),
    }
    response = boto3_fixtures.contrib.boto3.client("lambda").invoke(
        FunctionName=FunctionName, **{**defaults, **kwargs}
    )
    utils.check_status(response, keys=["StatusCode"])
    body = response["Payload"].read().decode("utf-8")
    try:
        body = json.loads(body)
    except Exception:
        pass
    utils.emit_logs(body)
    return response, body


def setup(lambdas: List[dict]):
    return {"lambdas": create_lambdas(lambdas)}


def teardown(lambdas: Dict[str, Lambda], **kwrags):
    destroy_lambdas(lambdas)


MockContext = namedtuple("Context", ["function_name"])
