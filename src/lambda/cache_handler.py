import json
from src.common.config import CustomLog, DatabaseConstants
from src.dynamodb.helper import GroupHelper, UserHelper


log = CustomLog().setup_logger()


def consumer(event, context):
    log.info(f'Lambda triggerd from SQS. Raw event: {event}')

    try:
        body = extract_body(event=event)
        json_body = json.loads(body)
        handle_message(body=json_body)
    except Exception as ex:  # improve: catch the particular exception
        log.error(f'Invalid message. This event will be send to DLQ. {ex}')
        raise ex


def extract_body(*, event: json) -> json:
    log.info('Extracting body')
    for record in event['Records']:
        if not record["body"]:
            raise ValueError('There is no body in this event!')
        else:
            return record["body"]


def handle_message(*, body: json):
    log.info('Handling message')
    if body["entityType"] == DatabaseConstants.ENTITY_TYPE_USER:
        log.info(f'Handling USER message {body["eventType"]}')
        UserHelper.handle_user(body=body)
    elif body["entityType"] == DatabaseConstants.ENTITY_TYPE_GROUP:
        log.info(f'Handling GROUP message {body["eventType"]}')
        GroupHelper.handle_group(body=body)