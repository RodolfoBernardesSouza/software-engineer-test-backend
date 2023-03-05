import json
import uuid
import hashlib
import boto3

from common.config import CustomLog
from common.config import Environment

env = Environment()
log = CustomLog().setup_logger()


class SNSPublisher:
    @staticmethod
    def publish(*, message: dict):
        if message["entityType"] == 'USER':
            if message["eventType"] == 'USER_DELETED':
                sns_event = UserSNSEventModel.build_user_delete_sns_event(message=message)
                log.info(f'publishing a USER DELETED event: {sns_event}')
            else:
                sns_event = UserSNSEventModel.build_user_sns_event(message=message)
                log.info(f'publishing a USER event: {sns_event}')
        else:
            sns_event = GroupSNSEventModel.build_group_sns_event(message=message)
            log.info(f'publishing a GROUP event: {sns_event}')

        client = boto3.client('sns')
        response = client.publish(
            TargetArn=env.sns_topic_arn,
            Message=json.dumps({'default': json.dumps(sns_event)}),
            MessageStructure='json'
        )
        log.info(f'message published: {response}')


class UserSNSEventModel:
    @staticmethod
    def build_user_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        user_data = dict({
            'name': message_event_data['name'],
            'email': message_event_data['email'],
            'groups': message_event_data['groups'],
            'password': UserSNSEventModel.__hash_password(password=message_event_data['password'])
        })
        return EnvelopModel.build_event_envelop(message=message,event_data=user_data)

    @staticmethod
    def build_user_delete_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        user_data = dict({
            'name': '',
            'email': message_event_data['email'],
            'groups': '',
            'password': ''
        })
        return EnvelopModel.build_event_envelop(message=message,event_data=user_data)

    @staticmethod
    def __hash_password(*, password: str) -> str:
        log.info('hashing password')
        byte_password = password.encode('utf-8')

        # Generate salt
        salt = uuid.uuid4().hex

        # Hash password
        password_hash_salt = hashlib.sha256(salt.encode() + byte_password).hexdigest() + ':' + salt
        #log.debug(f'byte_hash {password_hash_salt}')

        return password_hash_salt


class GroupSNSEventModel:

    @staticmethod
    def build_group_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        group_data = dict({
            'name': message_event_data['name']
        })
        return EnvelopModel.build_event_envelop(message=message,event_data=group_data)


class EnvelopModel:

    @staticmethod
    def build_event_envelop(*, message: dict, event_data: dict) -> dict:
        return dict({
            'entityType': message['entityType'],
            'eventType': message['eventType'],
            'eventData': event_data
        })
