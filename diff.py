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

        if data['kind'] == COMPANY:
            if not data['previous']:
                new_company_added(data['current'])
            elif data['diff']:
                # TODO: publish company changes using IFTT.publish_telegram_alert and IFTT.publish_twitter_alert
                print('COMPANY_DIFF', data['current']['id'], data['diff'])


def new_company_added(company):
    by_telegram = by([f'<a href="{z}">@{urlpath.URL(z).parts[1]}</a>' for x in company['data']['founders']
                      for y, z in x['social_links'].items() if y == 'twitter'])
    by_twitter = by([f'@{urlpath.URL(z).parts[1]}' for x in company['data']['founders'] for y, z in
                     x['social_links'].items() if y == 'twitter'])

    publish = False

    with deps.MONGO.start_session() as session, session.start_transaction():
        if not deps.MONGO_DB['company_posts'].find_one({'id': company['id']}, session=session):
            deps.MONGO_DB['company_posts'].insert_one({'id': company['id']}, session=session)
            publish = True

    if publish:
        print(deps.IFTTT.publish_twitter_alert(
            f'{company["data"]["name"]}{by_twitter} has just been added to {company["batch"]} batch<br><br>'
            f'More info: https://www.ycombinator.com/companies/{company["id"]}')
        )

        print(deps.IFTTT.publish_telegram_alert(
            f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a>{by_telegram} '
            f'has just been added to {company["batch"]} batch<br><br>'
            f'More info: https://www.ycombinator.com/companies/{company["id"]}')
        )


def by(twitters):
    result = ''
    if len(twitters) > 0:
        if len(twitters) == 1:
            by_handles = twitters[0]
        else:
            by_handles = ', '.join(twitters[:-1]) + ' and ' + twitters[-1]
        result = f' by {by_handles}'

    return result


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
