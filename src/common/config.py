import logging
from dataclasses import dataclass
from os import getenv
from logging import Logger


@dataclass
class Environment:
    aws_region: str = getenv('REGION')
    table_name: str = getenv('CACHE_TABLE')
    sns_topic_arn: str = 'arn:aws:sns:us-east-1:849681156123:software-engineer-test-backend-dev-messageTopic'


@dataclass
class DatabaseConstants:
    ENTITY_TYPE_USER = 'USER'
    ENTITY_TYPE_GROUP = 'GROUP'
    ENTITY_TYPE_GROUP_MEMBER = 'GROUP_MEMBER'


class CustomLog:

    @staticmethod
    def setup_logger() -> Logger:
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return logger
@dataclass
class JsonSchema:

#TODO add restrictions for empty atributes
        user_schema = {
            "$schema":"http://json-schema.org/draft-04/schema#",
            "type":"object",
            "properties":{
                "entityType":{"type":"string"},
                "eventType":{"type":"string"},
                "eventData":{
                    "type":"object",
                    "properties":{
                        "name":{"type":"string"},
                        "email":{"type":"string"},
                        "password":{"type":"string"},
                        "groups":{"type":"array","items":[{"type":"string"},{"type":"string"}]}
                    },
                    "required":[
                        "name",
                        "email",
                        "password",
                        "groups"
                    ]
                }
            },
            "required":[
                "entityType",
                "eventType",
                "eventData"
            ]
        }

#TODO add restrictions for empty atributes
        user_delete_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "entityType": {"type": "string"},
                "eventType": {"type": "string"},
                "eventData": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"}
                    },
                    "required": [
                        "email"
                    ]
                }
            },
            "required": [
                "entityType",
                "eventType",
                "eventData"
            ]
        }

#TODO add restrictions for empty atributes
        group_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "entityType": {"type": "string"},
                "eventType": {"type": "string"},
                "eventData": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": [
                        "name"
                    ]
                }
            },
            "required": [
                "entityType",
                "eventType",
                "eventData"
            ]
        }

