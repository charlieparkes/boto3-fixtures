import pytest

import boto3_fixtures as b3f


@pytest.mark.usefixtures("lam")
class TestMockLambdaMoto:
    def test_lambdas(self, set_environment, lambda_functions):
        for lam in lambda_functions:
            response, body = b3f.awslambda.invoke(
                FunctionName=lam["FunctionName"], Payload={"foo": "bar"},
            )
