"""
Module `sns` implements the setup and tear-down of SNS topics via boto3.

Example:
    >>> import boto3_fixtures as b3f
    >>> # ... setup `aws` fixture
    >>>
    >>> TOPICS = [
    >>>     "topic-1",
    >>>     {
    >>>         "TopicName": "topic-with-attrs",
    >>>         "Attributes": {"DisplayName": "Topic With Attributes"},
    >>>     }
    >>> ]
    >>> sns = b3f.contrib.pytest.service_fixture(sns, topics=TOPICS)
"""

import typing as T
from collections import namedtuple

import backoff
from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
import boto3_fixtures.utils as utils

SNSTopic = namedtuple("Topic", ["name", "arn", "response"])


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_topic(topic_config: dict) -> SNSTopic:
    resp = utils.call(
        boto3_fixtures.contrib.boto3.client("sns").create_topic, **topic_config
    )

    def _check_topic(arn):
        return boto3_fixtures.contrib.boto3.client("sns").get_topic_attributes(
            TopicArn=arn
        )

    utils.call(utils.backoff_check, func=lambda: _check_topic(resp["TopicArn"]))
    return SNSTopic(name=topic_config["Name"], arn=resp["TopicArn"], response=resp,)


def create_topics(topic_configs: T.List[dict]) -> T.Dict[str, SNSTopic]:
    topics = {}
    for config in topic_configs:
        tpc = create_topic(config)
        topics[tpc.name] = tpc
    return topics


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_topic(topic_arn: str):
    return utils.call(
        boto3_fixtures.contrib.boto3.client("sns").delete_topic, TopicArn=topic_arn
    )


def destroy_topics(topics: T.Dict[str, SNSTopic]):
    return [destroy_topic(tpc.arn) for tpc in topics.values()]


# --- Service interface ---


def setup(topics: T.List[T.Union[str, dict]] = None):
    if topics is None:
        return {"topic_arns": []}

    topic_configs = [{"Name": val} if isinstance(val, str) else val for val in topics]

    arns = create_topics(topic_configs)

    return {"topics": arns}


def teardown(**kwargs):
    return destroy_topics(kwargs["topics"])
