import json
import logging
import os
from contextlib import contextmanager

import backoff
from botocore.exceptions import ClientError

from boto3_fixtures.contrib import mindictive


def batch(iterable, n=1):
    """Batch iterator.

    https://stackoverflow.com/a/8290508

    """
    iter_len = len(iterable)
    for ndx in range(0, iter_len, n):
        yield iterable[ndx : min(ndx + n, iter_len)]


def _set_env(env):
    state = {}
    for k, v in env.items():
        state[k] = os.environ[k] if k in os.environ else None
        os.environ[k] = str(v)
        logging.getLogger().debug(f"os.environ[{k}] = {v}")
    return state


def _reset_env(env, state):
    for k, v in env.items():
        if k in state and state[k]:
            os.environ[k] = str(state[k])
        elif k in os.environ:
            del os.environ[k]


@contextmanager
def set_env(env):
    state = {}
    try:
        state = _set_env(env)
        yield
    finally:
        _reset_env(env, state)


def check_status(response, code=2, keys=["ResponseMetadata", "HTTPStatusCode"]):
    """Check status of an AWS API response."""
    status = mindictive.get_nested(response, keys)
    assert status // 100 == code
    return status


def call(_callable, *args, **kwargs):
    """Call boto3 function and check the AWS API response status code.

    Args:
        _callable (function): boto3 function to call
        *args: arguments to pass to _callable
        **kwargs: keyword args to pass to _callable

    Raises:
        AssertionError: if the _callable response status code is not in the 200 range
    """
    resp = _callable(*args, **kwargs)
    check_status(resp)
    return resp


def repr(o, attrs=[]):
    desc = ", ".join([f"{a}={getattr(o, a)}" for a in attrs])
    return f"{o.__class__.__name__}({desc})"


def describe_client_error(e):
    """Get the error code for a boto3 response exception."""
    return e.response.get("Error", {}).get("Code")


def exception_to_str(e):
    return f"{e.__class__.__name__} {e}"


@backoff.on_exception(backoff.expo, (TimeoutError, ClientError), max_time=30)
def backoff_check(func):
    return func()


def environment(
    fixtures: dict = {},
    sqs_queues: list = [],
    kinesis_streams: list = [],
    dynamodb_tables: list = [],
    s3_buckets: list = [],
):
    def clean(s):
        return s.upper().replace("-", "_")

    def env(**kwargs):
        vars = {
            "APP_ENVIRONMENT": "localstack",
            "AWS_DEFAULT_REGION": "us-east-1",
        }
        vars.update(fixtures)
        vars.update({clean(s): s for s in kinesis_streams})
        vars.update({clean(q): q for q in sqs_queues})
        vars.update({clean(q): q for q in s3_buckets})
        vars.update({clean(t["TableName"]): t["TableName"] for t in dynamodb_tables})
        will_overwrite = list(set(vars.keys()) & set(kwargs.keys()))
        if will_overwrite:
            logging.getLogger().warning(
                f"Your tests are going to overwrite the following fields: {will_overwrite}"
            )
        vars.update(kwargs)
        return vars

    return env


def emit_logs(body, logger=None):
    logger = logger if logger else logging.getLogger()
    if isinstance(body, dict) and "logs" in body:
        try:
            logs = json.loads(body["logs"])
        except TypeError:
            logs = body["logs"]
        for log in logs:
            logger.info(f"{log}")
    elif isinstance(body, str):
        logger.log(level=logging.INFO, msg=body)
