import boto3
import hashlib
import json

from boto3.dynamodb.conditions import Key, Attr
from src.common.config import Environment, CustomLog, DatabaseConstants

env = Environment()
log = CustomLog().setup_logger()
table_name = env.table_name
region = env.aws_region


class DynamoDBRepository:

    def __init__(self):
        item_table = boto3.resource('dynamodb', region_name=region)
        self.table = item_table.Table(table_name)

    # GROUP
    def save_group(self, *, event_data: dict):
        item = DatabaseModel.build_group_item(event_data=event_data)
        try:
            log.info(f'Saving a GROUP: {item}')
            self.__save_item(item=item)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not save the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_group(self, *, name: str) -> dict:
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            attribute_value=name
        )
        try:
            log.info(f'Reading a GROUP: {name}')
            return self.__get_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_GROUP)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_group_by_id(self, *, group_id: str) -> dict:
        try:
            log.info(f'Reading a GROUP with id: {group_id}')
            partition_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                entity_id=group_id
            )
            return self.__get_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_GROUP)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def delete_group_by_id(self, *, group_id: str):
        try:
            log.info(f'Deleting a GROUP with id: {group_id}')
            partition_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                entity_id=group_id
            )
            return self.__delete_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_GROUP)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not delete the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    # GROUP_MEMBER
    def retrieve_group_member_by_id(self, *, group_id: str, user_id: str) -> dict:
        try:
            log.info(f'Reading a GROUP_MEMBER for : {group_id} {user_id}')
            partition_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                entity_id=group_id
            )
            sort_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP_MEMBER,
                entity_id=user_id
            )
            return self.__get_item(partition_key=partition_key, sort_key=sort_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_group_members(self, *, group_id: str) -> dict:
        try:
            log.info(f'Reading all GROUP_MEMBERS for : {group_id}')
            partition_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                entity_id=group_id
            )
            return self.__get_items(partition_key=partition_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP_MEMBER. This event will be send to DLQ. {ex}')
            raise ex

    def create_group_member(self, *, group_id: str, email: str) -> dict:
        partition_key = DatabaseModel.build_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            entity_id=group_id
        )

        sort_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP_MEMBER,
            attribute_value=email
        )
        try:
            item = DatabaseModel.build_group_member(partition_key=partition_key, sort_key=sort_key)
            return self.__save_item(item=item)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not create the GROUP_MEMBER. This event will be send to DLQ. {ex}')
            raise ex

    def create_group_member_with_name_and_sort_key(self, *, name: str, sort_key: str) -> dict:
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            attribute_value=name
        )
        try:
            item = DatabaseModel.build_group_member(partition_key=partition_key, sort_key=sort_key)
            return self.__save_item(item=item)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not create the GROUP_MEMBER. This event will be send to DLQ. {ex}')
            raise ex

    def delete_group_member_by_keys(self, *, partition_key: str, sort_key: str) -> dict:
        try:
            return self.__delete_item(partition_key=partition_key, sort_key=sort_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not delete the GROUP_MEMBER. This event will be send to DLQ. {ex}')
            raise ex

    def delete_group_member_by_id(self, *, group_id: str, user_id: str) -> dict:
        partition_key = DatabaseModel.build_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            entity_id=group_id
        )

        sort_key = DatabaseModel.build_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP_MEMBER,
            entity_id=user_id
        )
        try:
            return self.__delete_item(partition_key=partition_key, sort_key=sort_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not delete the GROUP_MEMBER. This event will be send to DLQ. {ex}')
            raise ex

    # USER
    def save_user(self, *, event_data: dict):
        item = DatabaseModel.build_user_item(event_data=event_data)
        try:
            log.info(f'Saving a USER: {item}')
            self.__save_item(item=item)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not save the USER. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_user(self, *, email: str) -> dict:
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_USER,
            attribute_value=email
        )
        try:
            log.info(f'Reading a USER: {email}')
            return self.__get_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_USER)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the USER. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_user_by_id(self, *, user_id: str) -> dict:
        try:
            log.info(f'Reading a USER with id: {user_id}')
            partition_key = DatabaseModel.build_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_USER,
                entity_id=user_id
            )
            return self.__get_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_USER)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_user_by_key(self, *, user_partition_key: str) -> dict:
        try:
            log.info(f'Reading a USER with partition key: {user_partition_key}')
            return self.__get_item(partition_key=user_partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_USER)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the GROUP. This event will be send to DLQ. {ex}')
            raise ex

    def delete_user_by_id(self, *, user_id: str):
        log.info(f'Deleting a USER with id: {user_id}')
        partition_key = DatabaseModel.build_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_USER,
            entity_id=user_id
        )
        try:
            self.__delete_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_USER)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not delete the USER. This event will be send to DLQ. {ex}')
            raise ex

    def __save_item(self, *, item: dict):
        try:
            self.table.put_item(
                TableName=table_name,
                Item=item)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not save the item. This event will be send to DLQ. {ex}')
            raise ex

    def __get_item(self, *, partition_key: str, sort_key: str) -> dict:
        try:
            return self.table.get_item(Key={'partitionKey': partition_key, 'sortKey': sort_key})
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not retrieve the item. This event will be send to DLQ. {ex}')
            raise ex

    def __get_items(self, *, partition_key: str) -> dict:
        try:
            return self.table.query(KeyConditionExpression=Key('partitionKey').eq(partition_key))
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not retrieve the item. This event will be send to DLQ. {ex}')
            raise ex

    def __delete_item(self, *, partition_key: str, sort_key: str):
        try:
            self.table.delete_item(Key={'partitionKey': partition_key, 'sortKey': sort_key})
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not delete the item. This event will be send to DLQ. {ex}')
            raise ex


class DatabaseModel:

    @staticmethod
    def build_user_item(*, event_data: dict) -> dict:
        return dict({
            'partitionKey': DatabaseModel.create_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_USER,
                attribute_value=event_data['email']
            ),
            'sortKey': DatabaseConstants.ENTITY_TYPE_USER,
            'name': event_data['name'],
            'email': event_data['email'],
            'groups': event_data['groups'],
            'password': event_data['password']
        })

    @staticmethod
    def build_group_item(*, event_data: dict) -> dict:
        return dict({
            'partitionKey': DatabaseModel.create_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                attribute_value=event_data['name']
            ),
            'sortKey': DatabaseConstants.ENTITY_TYPE_GROUP,
            'name': event_data['name']
        })

    @staticmethod
    def build_group_member(*, partition_key: str, sort_key: str) -> dict:
        return dict({
            'partitionKey': partition_key,
            'sortKey': sort_key
        })

    @staticmethod
    def hash_name(*, name: str) -> str:
        byte_name = name.encode('utf-8')
        return f'{hashlib.sha256(byte_name).hexdigest()}'

    @staticmethod
    def create_key(*, partition_key_prefix: str, attribute_value: str) -> str:
        byte_attribute_value = attribute_value.encode('utf-8')
        return f'{partition_key_prefix}|{hashlib.sha256(byte_attribute_value).hexdigest()}'

    @staticmethod
    def build_key(*, partition_key_prefix: str, entity_id: str) -> str:
        return f'{partition_key_prefix}|{entity_id}'
