from typing import List

import dictdiffer


def generate_telegram(diffs, previous_company, current_company) -> List[str]:
    messages = []

    jobs = {
        'add': [],
        'remove': []
    }

    for diff in diffs:
        job_change(diff, previous_company, current_company, jobs)

    print(jobs)

    return messages


def job_change(diff, previous_company, current_company, jobs):
    if diff[0] == 'add':
        if diff[1] == 'data.jobs':
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
        if diff[1] == 'data.jobs':
            for (_, job) in diff[2]:
                jobs['remove'].append(job)
                # messages.append(
                #     f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a> '
                #     f'has just deleted job opening for <b>{job["title"]}</b> position in <b>{job["location"]}</b> '
                #     f'location'
                # )
