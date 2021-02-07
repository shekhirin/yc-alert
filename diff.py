import json
import os

import dictdiffer
import urlpath

import alert
import change
import deps

FACETS = 'FACETS'
BATCH = 'BATCH'
COMPANY = 'COMPANY'


def handler(event, context):
    for record in event['Records']:
        data = json.loads(record['body'])

        print(f'{data["kind"]}: {data["diff"]}')

        previous_company = dictdiffer.revert(data['diff'], data['current'])

        if data['kind'] == COMPANY:
            if not previous_company:
                new_company_added(data['current'])
            elif data['diff']:
                for message in change.generate_telegram(data['diff'], previous_company, data['current']):
                    print(deps.IFTTT.publish_change_telegram(message))



def new_company_added(company):
    publish = False

    with deps.MONGO.start_session() as session, session.start_transaction():
        if not deps.MONGO_DB['company_posts'].find_one({'id': company['id']}, session=session):
            deps.MONGO_DB['company_posts'].insert_one({'id': company['id']}, session=session)
            publish = True

    if publish:
        print(deps.IFTTT.publish_alert_twitter(alert.generate_twitter(company)))
        print(deps.IFTTT.publish_alert_telegram(alert.generate_telegram(company)))


def send(kind, previous, current):
    diff = None
    try:
        diff = list(dictdiffer.diff(previous, current, dot_notation=False))
    except RecursionError as e:
        print(e, previous, current)

    deps.SQS.send_message(
        QueueUrl=os.getenv('DIFFS_SQS_URL'),
        MessageBody=json.dumps({
            'kind': kind,
            'current': current,
            'diff': diff
        })
    )
