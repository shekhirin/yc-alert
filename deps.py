import os

import boto3
import pymongo
import requests
from algoliasearch.search_client import SearchClient
from mypy_boto3_sqs.client import SQSClient

ALGOLIA = SearchClient.create(os.getenv('ALGOLIA_APPLICATION_ID'), os.getenv('ALGOLIA_API_KEY')). \
    init_index('YCCompany_production')

MONGO = pymongo.MongoClient(os.getenv('MONGO_URL'))
MONGO_DB = MONGO['yc-alerts']

SQS: SQSClient = boto3.client('sqs')


class IFTTT:
    @staticmethod
    def publish_alert_telegram(text: str):
        return IFTTT.__publish('yc_alerts_telegram', text)

    @staticmethod
    def publish_alert_twitter(text: str):
        return IFTTT.__publish('yc_alerts_twitter', text)

    @staticmethod
    def publish_change_telegram(text: str):
        return IFTTT.__publish('yc_alerts_change_telegram', text)

    @staticmethod
    def publish_change_twitter(text: str):
        return IFTTT.__publish('yc_alerts_change_twitter', text)

    @staticmethod
    def __publish(trigger: str, text: str):
        return requests.post(
            f'https://maker.ifttt.com/trigger/{trigger}/with/key/{os.getenv("IFTTT_TOKEN")}',
            json={'value1': text}
        ).content
