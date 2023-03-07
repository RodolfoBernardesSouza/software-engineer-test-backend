import json
from src.common.config import CustomLog
from src.dynamodb.repository import DynamoDBRepository

log = CustomLog().setup_logger()


class GroupHelper:

    @staticmethod
    def handle_group(*, body: json):
        event_data = body['eventData']
        stored_group = DynamoDBRepository().retrieve_group(name=event_data['name'])
        log.info(f'stored_group: {stored_group}')
        if body["eventType"] == 'GROUP_CREATED':
            if 'Item' in stored_group.keys():
                log.error(f'GROUP already exists. {body["eventData"]}')
            else:
                DynamoDBRepository().save_group(event_data=body["eventData"])
        elif body["eventType"] == 'GROUP_UPDATED':
            if 'Item' in stored_group.keys():
                log.info(f'Not implemented')
                #FIXME: there is a dynamo error when retrieving the entire partition
                #stored_group_members = DynamoDBRepository().retrieve_group_members(name=event_data['name'])
                #log.info(f'stored_group_members: {stored_group_members}')
                #if not stored_group_members:
                #    DynamoDBRepository().save_group(event_data=body["eventData"])
                #else:
                #    log.error(f'GROUP can not be updated with users inside. {body["eventData"]}')
                    # The name of the GROUP is the Key. To UPDATE the group name I have to update all the users inside
                    # the group collection. This implementation is not relevant now.
                    # Meaning: YOU CAN NOT UPDATE GROUP WITH USERS INSIDE
            else:
                log.error(f'GROUP doesnt exist. {body["eventData"]}')
        elif body["eventType"] == 'GROUP_DELETED':
            if 'Item' in stored_group.keys():
                DynamoDBRepository().delete_group(name=event_data['name'])
            else:
                log.error(f'GROUP doesnt exist. {body["eventData"]}')


class UserHelper:

    @staticmethod
    def handle_user(*, body: json):
        log.info(f'Handling USER message {body["eventType"]}')