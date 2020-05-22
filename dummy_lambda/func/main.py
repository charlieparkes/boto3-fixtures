import logging


def handler(event, context):
    logger = logging.getLogger()
    logger.info("Hello World")
    return {"logs": [{"dummy": "message"}]}
