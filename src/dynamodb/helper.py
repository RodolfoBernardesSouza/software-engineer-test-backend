import json
from src.common.config import CustomLog
from src.dynamodb.repository import DynamoDBRepository, DatabaseModel

log = CustomLog().setup_logger()


class GroupHelper:

    @staticmethod
    def handle_group_create(*, event_data: json):
        stored_group = DynamoDBRepository().retrieve_group(name=event_data['name'])
        log.debug(f'stored_group: {stored_group}')
        if 'Item' in stored_group.keys():
            log.error(f'GROUP already exists. {event_data}')
        else:
            DynamoDBRepository().save_group(event_data=event_data)

    @staticmethod
    def handle_group_delete(*, event_data: json):
        group_id = event_data['id']
        stored_group = DynamoDBRepository().retrieve_group_by_id(group_id=group_id)
        if 'Item' in stored_group.keys():
            group_members = DynamoDBRepository().retrieve_group_members(group_id=group_id)
            if group_members['Count'] == 1:
                DynamoDBRepository().delete_group_by_id(group_id=group_id)
            else:
                log.error(f'It is not possible to delete a GROUP with a USER inside.')
        else:
            log.error(f'GROUP doesnt exist. {event_data}')

    @staticmethod
    def handle_group_update(*, event_data: json):
        group_id = event_data['id']
        new_name = event_data['name']
        stored_group = DynamoDBRepository().retrieve_group_by_id(group_id=group_id)
        stored_group_new_name = DynamoDBRepository().retrieve_group(name=new_name)

        if 'Item' in stored_group.keys() and 'Item ' not in stored_group_new_name.keys():
            group_members = DynamoDBRepository().retrieve_group_members(group_id=group_id)
            for group_member in group_members['Items']:
                if group_member['sortKey'].startswith("GROUP_MEMBER"):
                    DynamoDBRepository().delete_group_member_by_keys(partition_key=group_member['partitionKey'],
                                                                     sort_key=group_member['sortKey'])
                    DynamoDBRepository().create_group_member_with_name_and_sort_key(name=new_name,
                                                                                    sort_key=group_member['sortKey'])
                    # updating the user: It could be extracted as new method
                    user_partition_key = f'{"USER"}|{group_member["sortKey"].split("|")[1]}'
                    stored_user = DynamoDBRepository().retrieve_user_by_key(user_partition_key=user_partition_key)
                    if 'Item' in stored_user.keys():
                        stored_user_item = stored_user['Item']
                        stored_user_item['groups'].remove(group_id)
                        stored_user_item['groups'].append(DatabaseModel.hash_name(name=event_data['name']))
                        DynamoDBRepository().save_user(event_data=stored_user_item)

            DynamoDBRepository().delete_group_by_id(group_id=group_id)
            DynamoDBRepository().save_group(event_data=event_data)

        elif 'Item' in stored_group_new_name.keys():
            log.error(f'Group with name {event_data["name"]}, already exists. {event_data}')
        else:
            log.error(f'GROUP doesnt exist. {event_data}')


class UserHelper:

    @staticmethod
    def __is_group_list_different(*, stored_user_item: dict, event_data: dict) -> bool:
        stored_user_item_group_list = stored_user_item['groups'].sort()
        event_data_group_list = event_data['groups'].sort()
        if stored_user_item_group_list != event_data_group_list:
            return True
        else:
            return False

    @staticmethod
    def __all_groups_exist(*, event_data: json) -> bool:
        for group_id in event_data["groups"]:
            stored_group = DynamoDBRepository().retrieve_group_by_id(group_id=group_id)
            if 'Item' not in stored_group.keys():
                log.error(f'The group with id. {group_id} does not exist. User not created.')
                return False
        return True

    @staticmethod
    def handle_user_create(*, event_data: json):
        stored_user = DynamoDBRepository().retrieve_user(email=event_data['email'])
        if 'Item' in stored_user.keys():
            log.error(f'USER already exists. {event_data}')
        else:
            if UserHelper.__all_groups_exist(event_data=event_data):
                DynamoDBRepository().save_user(event_data=event_data)
                for group_id in event_data["groups"]:
                    DynamoDBRepository().create_group_member(group_id=group_id, email=event_data['email'])

    @staticmethod
    def handle_user_delete(*, event_data: json):
        user_id = event_data['id']
        stored_user = DynamoDBRepository().retrieve_user_by_id(user_id=user_id)
        if 'Item' not in stored_user.keys():
            log.error(f'USER with id {user_id} does not exists.')
        else:
            stored_user_item = stored_user['Item']
            for group_id in stored_user_item["groups"]:
                stored_group = DynamoDBRepository().retrieve_group_member_by_id(group_id=group_id, user_id=user_id)
                if 'Item' not in stored_group.keys():
                    log.error(f'The GROUP_MEMBER does not exists, when deleting the user.')
                else:
                    DynamoDBRepository().delete_group_member_by_id(group_id=group_id, user_id=user_id)
            DynamoDBRepository().delete_user_by_id(user_id=user_id)

    @staticmethod
    def handle_user_update(*, event_data: json):
        user_id = event_data['id']
        stored_user = DynamoDBRepository().retrieve_user_by_id(user_id=user_id)
        if 'Item' not in stored_user.keys():
            log.error(f'USER with id {user_id} does not exists.')
        elif not UserHelper.__all_groups_exist(event_data=event_data):
            log.error(f'Invalid group list.')
        else:
            stored_user_item = stored_user['Item']
            for group_id in stored_user_item["groups"]:
                stored_group = DynamoDBRepository().retrieve_group_member_by_id(group_id=group_id, user_id=user_id)
                if 'Item' not in stored_group.keys():
                    log.error(f'The GROUP_MEMBER does not exists, when deleting the user.')
                else:
                    DynamoDBRepository().delete_group_member_by_id(group_id=group_id, user_id=user_id)
            DynamoDBRepository().delete_user_by_id(user_id=user_id)
            DynamoDBRepository().save_user(event_data=event_data)
            for group_id in event_data["groups"]:
                DynamoDBRepository().create_group_member(group_id=group_id, email=event_data['email'])
