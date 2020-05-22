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
from contextlib import contextmanager
from pathlib import Path

import boto3_fixtures.contrib.boto3
from boto3_fixtures import utils


def create(
    name: str = "my_lambda",
    runtime: str = "python3.8",
    role: str = "foobar",
    handler: str = "main.lambda_handler",
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


def destroy(name: str = "my_lambda", **kwargs):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("lambda").delete_function, FunctionName=name
    )


def invoke(name: str = "my_lambda", payload: dict = {}, **kwargs):
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
    testing_utils.emit_logs(body)
    return response, body


@contextmanager
def setup(**kwargs):
    try:
        yield create(**kwargs)
    finally:
        destroy(**kwargs)


MockContext = namedtuple("Context", ["function_name"])


class MockPayload:
    @classmethod
    def sqs(payloads):
        def fmt(p):
            return {"body": json.dumps(p)}

        records = [fmt(p) for p in payloads]
        return {"Records": records}

    @classmethod
    def kinesis(payloads):
        def fmt(p):
            return {
                "kinesis": {
                    "data": str(base64.b64encode(json.dumps(p).encode()), "utf-8")
                }
            }

        records = [fmt(p) for p in payloads]
        return {"Records": records}
