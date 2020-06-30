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

import backoff
import typing as T

from botocore.exceptions import ClientError

import boto3_fixtures.contrib.boto3
import boto3_fixtures.utils as utils

TopicList = T.List[T.Union[str, dict]]


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def create_topics(topic_config_list: T.List[dict]) -> T.List[str]:
    sns = boto3_fixtures.contrib.boto3.client("sns")
    arns = []
    for tpc_config in topic_config_list:
        resp = utils.call(sns.create_topic, **tpc_config)

        def _check_topic(arn):
            return boto3_fixtures.contrib.boto3.client("sns").get_topic_attributes(
                TopicArn=arn
            )

        utils.call(utils.backoff_check, func=lambda: _check_topic(resp["TopicArn"]))

        arns.append(resp["TopicArn"])
    return arns


@backoff.on_exception(backoff.expo, ClientError, max_time=30)
def destroy_topics(topic_arn_list: T.List[str]):
    sns = boto3_fixtures.contrib.boto3.client("sns")
    for arn in topic_arn_list:
        utils.call(sns.delete_topic, TopicArn=arn)


# --- Service interface ---

def setup(topics: T.Optional[TopicList] = None):
    if topics is None:
        return {"topic_arns": []}

    topic_configs = [
        {"Name": val} if isinstance(val, str) else val
        for val in topics
    ]

    arns = create_topics(topic_configs)

    return {"topic_arns": arns}


def teardown(**kwargs):
    destroy_topics(kwargs["topic_arns"])
