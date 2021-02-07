from typing import List


def generate_telegram(diffs, previous_company, current_company) -> List[str]:
    messages = []

    jobs = {
        'add': [],
        'remove': []
    }

    meta = {
        'change': []
    }

    for diff in diffs:
        jobs_change(diff, previous_company, current_company, jobs)
        meta_change(diff, previous_company, current_company, meta)

    jobs['add'] = unique_dicts(jobs['add'], 'apply')
    jobs['remove'] = unique_dicts(jobs['remove'], 'apply')

    print('CHANGES:', jobs, meta)

    return messages


def jobs_change(diff, previous_company, current_company, jobs):
    if diff[0] == 'add':
        if diff[1] == ['data', 'jobs']:
            for (_, job) in diff[2]:
                jobs['add'].append(job)
                # messages.append(
                #     f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a> '
                #     f'has just added job opening for <b>{job["title"]}</b> position in <b>{job["location"]}</b> '
                #     f'location<br><br>'
                #     f'Apply here: {job["apply"]}'
                # )
    elif diff[0] == 'change':
        if diff[1][:2] == ['data', 'jobs'] and diff[1][-1] == 'apply':
            idx = diff[1][2]
            jobs['add'].append(current_company['data']['jobs'][idx])
            jobs['remove'].append(previous_company['data']['jobs'][idx])
    elif diff[0] == 'remove':
        if diff[1] == ['data', 'jobs']:
            for (_, job) in diff[2]:
                jobs['remove'].append(job)
                # messages.append(
                #     f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a> '
                #     f'has just deleted job opening for <b>{job["title"]}</b> position in <b>{job["location"]}</b> '
                #     f'location'
                # )


def meta_change(diff, previous_company, current_company, meta):
    if diff[0] == 'change':
        if (name := diff[1][-1]) and name in ('name', 'headline', 'description'):
            meta['change'].append({name: diff[2]})


def unique_dicts(dicts, key):
    return list({x[key]: x for x in dicts}.values())
