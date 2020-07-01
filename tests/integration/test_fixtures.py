import pytest
import tests.utils


@pytest.mark.usefixtures("localstack")
class TestMockWithLocalstack:
    @pytest.mark.usefixtures("kinesis")
    def test_kinesis_fixtures(self, kinesis_streams):
        tests.utils.check_kinesis_fixtures(kinesis_streams)

    @pytest.mark.usefixtures("sqs")
    def test_sqs_fixtures(self, sqs_queues):
        tests.utils.check_sqs_fixtures(sqs_queues)

    @pytest.mark.usefixtures("dynamodb")
    def test_dynamodb_fixtures(self, dynamodb_tables):
        tests.utils.check_dynamodb_fixtures(dynamodb_tables)

    @pytest.mark.usefixtures("s3")
    def test_s3_fixtures(self, s3_buckets):
        tests.utils.check_s3_fixtures(s3_buckets)

    @pytest.mark.usefixtures("lam")
    def test_lambda_fixtures(self, lambda_functions):
        tests.utils.check_lambda_fixtures(lambda_functions)

    @pytest.mark.usefixtures("sns")
    def test_sns_fixtures(self, sns_topics):
        tests.utils.check_sns_fixtures(sns_topics)
