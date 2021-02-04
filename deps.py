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
    def publish(text):
        return requests.post(f'https://maker.ifttt.com/trigger/yc_alerts/with/key/{os.getenv("IFTTT_TOKEN")}', json={
            "value1": text
        }).content
