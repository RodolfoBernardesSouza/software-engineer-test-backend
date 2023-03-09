import json
import uuid
import hashlib
import boto3

from src.common.config import CustomLog
from src.common.config import Environment

env = Environment()
log = CustomLog().setup_logger()


class SNSPublisher:
    @staticmethod
    def publish(*, message: dict):
        log.info(f'publishing a {message["entityType"]} event: {message["eventType"]}')
        sns_event = message
        if message["entityType"] == 'USER':
            if message["eventType"] == 'USER_DELETED':
                sns_event = UserSNSEventModel.build_user_delete_sns_event(message=message)
            elif message["eventType"] == 'USER_UPDATED':
                sns_event = UserSNSEventModel.build_user_update_sns_event(message=message)
            elif message["eventType"] == 'USER_CREATED':
                sns_event = UserSNSEventModel.build_user_sns_event(message=message)
        else:
            if message["eventType"] == 'GROUP_UPDATED':
                sns_event = GroupSNSEventModel.build_group_update_sns_event(message=message)
            elif message["eventType"] == 'GROUP_CREATED':
                sns_event = GroupSNSEventModel.build_group_sns_event(message=message)
            elif message["eventType"] == 'GROUP_DELETED':
                sns_event = GroupSNSEventModel.build_group_delete_sns_event(message=message)

        SNSPublisher.__send(sns_event=sns_event)

    @staticmethod
    def __send(*, sns_event: dict):
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
        return EnvelopModel.build_event_envelop(message=message, event_data=user_data)

    @staticmethod
    def build_user_update_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        user_data = dict({
            'name': message_event_data['name'],
            'id': message_event_data['id'],
            'email': message_event_data['email'],
            'groups': message_event_data['groups'],
            'password': UserSNSEventModel.__hash_password(password=message_event_data['password'])
        })
        return EnvelopModel.build_event_envelop(message=message, event_data=user_data)

    @staticmethod
    def build_user_delete_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        user_data = dict({
            'name': '',
            'id': message_event_data['id'],
            'groups': '',
            'password': ''
        })
        return EnvelopModel.build_event_envelop(message=message, event_data=user_data)

    @staticmethod
    def __hash_password(*, password: str) -> str:
        log.info('hashing password')
        byte_password = password.encode('utf-8')

        # Generate salt
        salt = uuid.uuid4().hex

        # Hash password
        password_hash_salt = hashlib.sha256(salt.encode() + byte_password).hexdigest() + ':' + salt
        # log.debug(f'byte_hash {password_hash_salt}')

        return password_hash_salt


class GroupSNSEventModel:

    @staticmethod
    def build_group_update_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        group_data = dict({
            'name': message_event_data['name'],
            'id': message_event_data['id']
        })
        return EnvelopModel.build_event_envelop(message=message, event_data=group_data)

    @staticmethod
    def build_group_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        group_data = dict({
            'name': message_event_data['name']
        })
        return EnvelopModel.build_event_envelop(message=message, event_data=group_data)

    @staticmethod
    def build_group_delete_sns_event(*, message: dict) -> dict:
        message_event_data = message['eventData']
        group_data = dict({
            'id': message_event_data['id']
        })
        return EnvelopModel.build_event_envelop(message=message, event_data=group_data)


class EnvelopModel:

    @staticmethod
    def build_event_envelop(*, message: dict, event_data: dict) -> dict:
        return dict({
            'entityType': message['entityType'],
            'eventType': message['eventType'],
            'eventData': event_data
        })
