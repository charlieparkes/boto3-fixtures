ENV = {"AWS_DEFAULT_REGION": "us-east-1", "FUNCTION_NAME": "my_lambda"}


# AWS Fixtures
S3 = ["first-bucket", "second-bucket"]

SQS = [
    "first-queue",
    "second-queue",
    {"QueueName": "third-queue", "Attributes": {"RedrivePolicy": {}}},
]

KINESIS = ["first-stream", "second-stream"]

DYNAMODB = [
    {
        "AttributeDefinitions": [
            {"AttributeName": "uri", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        "TableName": "test-dbd-table",
        "KeySchema": [
            {"AttributeName": "uri", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
    }
]

LAMBDA = [
    {
        "zip_path": "dummy_lambda/dist/build.zip",
        "FunctionName": "my_lambda",
        "Runtime": "python3.6",
        "Environment": {"test_bool_env_var": True},
    }
]

SNS = [
    "topic-1",
    {
        "Name": "topic-with-tags",
        "Tags": [
            {"Key": "tag", "Value": "hello"}
        ]
    }
]
