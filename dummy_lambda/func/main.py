import logging

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.info("Hello World")
    return True
