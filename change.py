from typing import List, Callable


def generate_telegram(diffs, previous_company, current_company) -> List[str]:
    change_functions: List[Callable[[List, dict, dict], List[str]]] = [
        jobs_change,
        meta_change
    ]

    messages = []

    for diff in diffs:
        for change in change_functions:
            messages.extend(change(diff, previous_company, current_company))

    print('MESSAGES:', messages)

    return messages


def jobs_change(diff: List, previous_company: dict, current_company: dict) -> List[str]:
    jobs = {
        'add': [],
        'remove': []
    }

    if diff[0] == 'add':
        if diff[1] == ['data', 'jobs']:
            for (_, job) in diff[2]:
                jobs['add'].append(job)
    elif diff[0] == 'change':
        if diff[1][:2] == ['data', 'jobs'] and diff[1][-1] == 'apply':
            idx = diff[1][2]
            jobs['add'].append(current_company['data']['jobs'][idx])
            jobs['remove'].append(previous_company['data']['jobs'][idx])
    elif diff[0] == 'remove':
        if diff[1] == ['data', 'jobs']:
            for (_, job) in diff[2]:
                jobs['remove'].append(job)

    jobs['add'] = unique_dicts(jobs['add'], 'apply')
    jobs['remove'] = unique_dicts(jobs['remove'], 'apply')

    print('JOBS:', jobs)

    messages = []

    for job in jobs['add']:
        messages.append(
            f'<a href="{current_company["data"]["links"][0]}">{current_company["data"]["name"]}</a> '
            f'has just added job opening for <b>{job["title"]}</b> position in <b>{job["location"]}</b> '
            f'location<br><br>'
            f'Apply here: {job["apply"]}'
        )

    for job in jobs['remove']:
        messages.append(
            f'<a href="{current_company["data"]["links"][0]}">{current_company["data"]["name"]}</a> '
            f'has just deleted job opening for <b>{job["title"]}</b> position in <b>{job["location"]}</b> '
            f'location'
        )

    return messages


def meta_change(diff: List, previous_company: dict, current_company: dict) -> List[str]:
    meta = {
        'add': {},
        'change': {},
        'remove': {}
    }

    if diff[0] == 'change':
        if (name := diff[1][-1]) and name in ('name', 'headline', 'description'):
            previous, current = diff[2]
            if not previous:
                meta['add'][name] = diff[2]
            elif not current:
                meta['remove'][name] = diff[2]
            else:
                meta['change'][name] = diff[2]

    print('META:', meta)

    messages = []

    for name, (_, current) in meta['add'].items():
        messages.append(
            f'<a href="{current_company["data"]["links"][0]}">{current_company["data"]["name"]}</a> '
            f'has just added {name}: <b>{current}</b>'
        )

    for name, (previous, current) in meta['change'].items():
        messages.append(
            f'<a href="{current_company["data"]["links"][0]}">{current_company["data"]["name"]}</a> '
            f'has just changed {name} from <b>{previous}</b> to <b>{current}</b>'
        )

    for name, (previous, _) in meta['remove'].items():
        messages.append(
            f'<a href="{current_company["data"]["links"][0]}">{current_company["data"]["name"]}</a> '
            f'has just removed {name}. Previously it was <b>{previous}</b>'
        )

    return messages


def unique_dicts(dicts, key):
    return list({x[key]: x for x in dicts}.values())
