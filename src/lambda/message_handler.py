import sys
import json
from src.common.config import CustomLog, JsonSchema
from src.sns.publisher import SNSPublisher

sys.path.insert(0, '3pp_lib/vendor')
import jsonschema

log = CustomLog().setup_logger()
user_schema = JsonSchema().user_schema
user_delete_schema = JsonSchema().user_delete_schema
user_update_schema = JsonSchema().user_update_schema
group_schema = JsonSchema().group_schema
group_update_schema = JsonSchema().group_update_schema
group_delete_schema = JsonSchema().group_delete_schema


def consumer(event, context):
    log.info(f'Lambda triggerd from SQS. Raw event: {event}')
    try:
        body = extract_body(event=event)
        json_body = json.loads(body)
        validate_body(body=json_body)
    except Exception as ex:  # improve: catch the particular exception
        log.error(f'Invalid message. This event will be send to DLQ. {ex}')
        raise ex

    log.info(f'Given JSON data is Valid {json_body}')
    SNSPublisher().publish(message=json_body)


def extract_body(*, event: json) -> json:
    log.info('Extracting body')
    for record in event['Records']:
        if not record["body"]:
            raise ValueError('There is no body in this event!')
        else:
            return record["body"]


def validate_body(*, body: json):
    log.info(f'Validating json. entityType: {body["entityType"]} eventType: {body["eventType"]}')
    try:
        if body["entityType"] == 'USER':
            if body["eventType"] == 'USER_DELETED':
                jsonschema.validate(instance=body, schema=user_delete_schema)
            elif body["eventType"] == 'USER_UPDATED':
                jsonschema.validate(instance=body, schema=user_update_schema)
            elif body["eventType"] == 'USER_CREATED':
                jsonschema.validate(instance=body, schema=user_schema)
        elif body["entityType"] == 'GROUP':
            if body["eventType"] == 'GROUP_UPDATED':
                jsonschema.validate(instance=body, schema=group_update_schema)
            elif body["eventType"] == 'GROUP_CREATED':
                jsonschema.validate(instance=body, schema=group_schema)
            elif body["eventType"] == 'GROUP_DELETED':
                jsonschema.validate(instance=body, schema=group_delete_schema)
        else:
            log.error(f'Invalid entityType. {body["entityType"]}')
            raise ValueError('Invalid entityType.')
    except jsonschema.exceptions.ValidationError as err:
        raise ValueError(err)
