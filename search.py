import os

import deps
import diff

QUERY_FACETS = ['top_company', 'isHiring', 'nonprofit', 'batch', 'industries', 'subindustry', 'status', 'regions']


def handler(event, context):
    response = deps.ALGOLIA.search('', {
        'hitsPerPage': 0,
        'facets': QUERY_FACETS
    })

    current_facets = response.get('facets')
    if not current_facets:
        return

    with deps.MONGO.start_session() as session, session.start_transaction():
        previous_facets = deps.MONGO_DB['facets_snapshots'].find_one({
            '$query': {},
            '$orderby': {'$natural': -1}
        }, session=session) or {}
        previous_facets.pop('_id', None)

        if previous_facets != current_facets:
            # diff.send(diff.FACETS, previous_facets, current_facets)

            deps.MONGO_DB['facets_snapshots'].insert_one(current_facets, session=session)

    for batch_name, count in current_facets.get('batch', {}).items():
        # if (previous_count := previous_facets.get('batch', {}).get(batch_name)) and previous_count != count:
        if True:
            deps.SQS.send_message(
                QueueUrl=os.getenv('BATCHES_SQS_URL'),
                MessageBody=batch_name
            )
