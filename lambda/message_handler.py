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
        body = json.loads(record["body"])
        name = body['name']  # validar o nome, o email e a senha ver se algum dos campos está vazio, dentro de um try catch
        logger.info(name)



