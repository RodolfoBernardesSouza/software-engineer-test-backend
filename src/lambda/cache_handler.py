import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def consumer(event, context):
    logger.info(f'raw event: {event}')
    for record in event['Records']:
        logger.info(f'Message body: {record["body"]}')
        #logger.info(f'Message attribute: {record["messageAttributes"]["AttributeName"]["stringValue"]}')




