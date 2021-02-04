import json
import os

import dictdiffer
import urlpath

import deps

FACETS = 'FACETS'
BATCH = 'BATCH'
COMPANY = 'COMPANY'


def handler(event, context):
    for record in event['Records']:
        data = json.loads(record['body'])

        print(f'{data["kind"]}: {data["diff"]}')

        if data['kind'] == COMPANY and not data['previous']:
            new_company_added(data['current'])


def new_company_added(company):
    founder_twitters = [f'<a href="{z}">@{urlpath.URL(z).parts[1]}</a>' for x in company['data']['founders'] for y, z in
                        x['social_links'].items() if y == 'twitter']

    by = ''
    if len(founder_twitters) > 0:
        if len(founder_twitters) == 1:
            by_handles = founder_twitters[0]
        else:
            by_handles = ', '.join(founder_twitters[:-1]) + ' and ' + founder_twitters[-1]
        by = f' by {by_handles}'

    with deps.MONGO.start_session() as session, session.start_transaction():
        if not deps.MONGO_DB['company_tweets'].find_one({'id': company['id']}, session=session):
            deps.MONGO_DB['company_tweets'].insert_one({'id': company['id']}, session=session)
            print(deps.IFTTT.publish(f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a>{by} '
                                     f'has just been added to {company["batch"]} batch<br><br>'
                                     f'More info: https://www.ycombinator.com/companies/{company["id"]}'))


def send(kind, previous, current, include_previous=False, include_current=False):
    diff = None
    try:
        diff = list(dictdiffer.diff(previous, current))
    except RecursionError as e:
        print(e, previous, current)

    deps.SQS.send_message(
        QueueUrl=os.getenv('DIFFS_SQS_URL'),
        MessageBody=json.dumps({
            'kind': kind,
            'previous': previous if not previous or include_previous else 'exists',
            'current': current if not current or include_current else 'exists',
            'diff': diff
        })
    )
