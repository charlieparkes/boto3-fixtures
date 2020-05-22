import pytest

import boto3_fixtures as b3f


@pytest.mark.usefixtures("lam_localstack")
class TestMockLambdaLocalstack:
    def test_lambdas(self, set_environment, lambda_functions):
        for lam in lambda_functions:
            response, body = b3f.awslambda.invoke(
                name=lam["name"], payload={"foo": "bar"},
            )
