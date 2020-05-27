# import moto
# import pytest
#
# import tests.utils
# from boto3_fixtures.contrib.pytest import generate_fixture
# from tests import fixtures


# with_sqs = generate_fixture("sqs", decorator=moto.mock_sqs, scope="class", **fixtures.SQS)

# contrib_sqs = generate_fixture("sqs", scope="class", **fixtures.SQS)
#
# @pytest.fixture
# def with_sqs(localstack, contrib_sqs):
#     yield

# @pytest.mark.usefixtures("with_sqs")
# def test_sqs_fixtures(sqs_queues):
#     tests.utils.check_sqs_fixtures(sqs_queues)
