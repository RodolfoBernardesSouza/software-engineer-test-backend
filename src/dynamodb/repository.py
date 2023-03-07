import boto3
import hashlib


from src.common.config import Environment, CustomLog, DatabaseConstants

env = Environment()
log = CustomLog().setup_logger()
table_name = env.table_name
region = env.aws_region


class DynamoDBRepository:

    def __init__(self):
        self.item_table = boto3.resource('dynamodb', region_name=region)
        self.table = self.item_table.Table(table_name)

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

    def retrieve_group_members(self, *, name: str) -> dict:
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            attribute_value=name
        )
        try:
            return self.__get_items(partition_key=partition_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the USER. This event will be send to DLQ. {ex}')
            raise ex

    def retrieve_group_member(self, *, nome: str, email: str) -> dict:
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            attribute_value=nome
        )
        sort_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP_MEMBER,
            attribute_value=email
        )
        try:
            return self.__get_item(partition_key=partition_key, sort_key=sort_key)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'Could not retrieve the USER. This event will be send to DLQ. {ex}')
            raise ex

    def delete_group(self, *, name: str):
        partition_key = DatabaseModel.create_key(
            partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
            attribute_value=name
        )
        try:
            log.info(f'Deleting a GROUP: {name}')
            return self.__delete_item(partition_key=partition_key, sort_key=DatabaseConstants.ENTITY_TYPE_GROUP)
        except Exception as ex:  # improve: catch the particular exception
            log.error(f'could not delete the GROUP. This event will be send to DLQ. {ex}')
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

    #FIXME getting error from batch_get_item
    def __get_items(self, *, partition_key: str) -> dict:
        try:
            get_items_return = self.item_table.batch_get_item(
                RequestItems={
                    table_name: {
                        'Keys': [{'partitionKey': partition_key}]
                    }})
            #Keys={'partitionKey': partition_key})
            log.info(f'get_items_return: {get_items_return["Responses"]}')
            return get_items_return
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
    def build_user_item(*, message: dict) -> dict:
        return dict({
            'partitionKey': message['email'] + 'partitionkey',
            'sortKey': message['email'] + 'sortkey',
            'name': message['name'],
            'email': message['email'],
            'groups': message['groups'],
            'password': message['password']
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
    def build_group_member(*, name: str, email: str) -> dict:
        return dict({
            'partitionKey': DatabaseModel.create_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP,
                attribute_value=name
            ),
            'sortKey': DatabaseModel.create_key(
                partition_key_prefix=DatabaseConstants.ENTITY_TYPE_GROUP_MEMBER,
                attribute_value=email)
        })

    @staticmethod
    def create_key(*, partition_key_prefix: str, attribute_value: str) -> str:
        byte_attribute_value = attribute_value.encode('utf-8')
        return f'{partition_key_prefix}|{hashlib.sha256(byte_attribute_value).hexdigest()}'
