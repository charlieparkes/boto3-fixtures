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

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_lambda(
    name: str,
    runtime: str,
    role: str = "foobar",
    handler: str = "main.handler",
    path: str = "dist/build.zip",
    environment: dict = {},
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

    with open(str(Path().absolute() / path), "rb") as f:
        zipped_code = f.read()
        utils.call(
            boto3_fixtures.contrib.boto3.client("lambda").create_function,
            FunctionName=name,
            Runtime=runtime,
            Role=role,
            Handler=handler,
            Code=dict(ZipFile=zipped_code),
            Timeout=300,
            Environment={"Variables": clean_env(environment)},
        )


def create_lambdas(configs):
    for c in configs:
        create_lambda(**c)


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_lambda(name: str, **kwargs):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("lambda").delete_function, FunctionName=name
    )


def destroy_lambdas(configs):
    for c in configs:
        destroy_lambda(**c)


def invoke(name: str, payload: dict = {}, **kwargs):
    defaults = {
        "InvocationType": "RequestResponse",
        "LogType": "Tail",
        "Payload": json.dumps(payload).encode(),
    }
    response = boto3_fixtures.contrib.boto3.client("lambda").invoke(
        FunctionName=name, **{**defaults, **kwargs}
    )
    utils.check_status(response, keys=["StatusCode"])
    body = response["Payload"].read().decode("utf-8")
    try:
        body = json.loads(body)
    except Exception:
        pass
    utils.emit_logs(body)
    return response, body


def setup(configs):
    create_lambdas(configs)
    return {"configs": configs}


def teardown(configs):
    destroy_lambdas(configs)


MockContext = namedtuple("Context", ["function_name"])
