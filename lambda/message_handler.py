import sys

sys.path.insert(0, 'src/vendor')
import jsonschema

import json

from common.config import CustomLog
from common.config import JsonSchema

log = CustomLog().setup_logger()
user_schema = JsonSchema().user_schema
user_delete_schema = JsonSchema().user_delete_schema
group_schema = JsonSchema().group_schema

def consumer(event, context):
    log.info(f'Lambda triggerd from SQS. Raw event: {event}')

    try:
        body = extract_body(event=event)
        log.info('loading json')
        json_body = json.loads(body)
        validate_body(body=json_body)
    except Exception as ex: #improve: catch teh particular exception
        log.info(f'Invalid message. This event will be send to DLQ. {ex}')
        raise ex

    log.info('Given JSON data is Valid')
    log.info('Chamar função que vai fazer hash na senha')

def extract_body(*, event: json) ->json:
    log.info('Extracting body')
    for record in event['Records']:
        log.info(f'Body {record["body"]}')
        if not record["body"]:
            raise ValueError('There is no body in this event!')
        else:
            return record["body"]
def validate_body(*, body: json):
    log.info('Validating json')
    try:
        if body["entityType"] == 'USER':
            log.info(f'entityType: {body["entityType"]}')
            if body["eventType"] == 'USER_DELETED':
                log.info(f'eventType: {body["eventType"]}')
                jsonschema.validate(instance=body, schema=user_delete_schema)
            else:
                log.info(f'eventType: {body["eventType"]}')
                jsonschema.validate(instance=body, schema=user_schema)
        elif body["entityType"] == 'GROUP':
            log.info(f'entityType {body["eventType"]}')
            jsonschema.validate(instance=body, schema=group_schema)
        else:
            log.error(f'Invalid entityType. {body["entityType"]}')
            raise ValueError('Invalid entityType.')
    except jsonschema.exceptions.ValidationError as err:
        raise ValueError(err)

