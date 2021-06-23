import json
import os

import deps
import diff


def handler(event, context):
    for record in event['Records']:
        batch_name = record['body']
        response = deps.ALGOLIA.search('', {
            'hitsPerPage': 1000,
            'facetFilters': [f'batch:{batch_name}']
        })

        hits = response.get('hits', [])

        current_batch = {'batch': batch_name, 'hits': hits}

        with deps.MONGO.start_session() as session, session.start_transaction():
            previous_batch = deps.MONGO_DB['batch_snapshots'].find_one({
                '$query': {'batch': batch_name},
                '$orderby': {'$natural': -1}
            }, session=session) or {}
            previous_batch.pop('_id', None)

            if previous_batch != current_batch:
                # diff.send(diff.BATCH, previous_batch, current_batch)

                deps.MONGO_DB['batch_snapshots'].insert_one(current_batch, session=session)

        for hit in hits:
            hit_id = hit.get('id')
            hit_slug = hit.get('slug')
            if not (hit_id and hit_slug):
                continue

            deps.SQS.send_message(
                QueueUrl=os.getenv('COMPANIES_SQS_URL'),
                MessageBody=json.dumps({'id': hit_id, 'slug': hit_slug, 'batch': batch_name})
            )
