import json

import requests
from bs4 import BeautifulSoup

import deps
import diff


def handler(event, context):
    for record in event['Records']:
        data = json.loads(record['body'])
        company_id, batch_name = data['id'], data['batch']

        page = BeautifulSoup(requests.get(f'https://www.ycombinator.com/companies/{company_id}').content,
                             features="html.parser")

        current_company = {
            'id': company_id,
            'batch': batch_name,
            'data': {
                'logo_url': '',
                'pills': {
                    'orange': '',
                    'industries': [],
                    'others': []
                },
                'name': '',
                'headline': '',
                'description': '',
                'links': [],
                'facts': [],
                'social_links': {},
                'active_founders': [],
                'former_founders': [],
                'jobs': []
            }
        }

        content = page.find('div', class_='content')
        for section in content.find_all('section'):
            aside = section.find('aside').text

            if aside == 'About':
                main_box_items = section.find('div', class_='main-box').find_all('div', recursive=False)

                main_box_flex_row_items = main_box_items[0].find_all('div', recursive=False)
                if img := main_box_flex_row_items[0].find('img'):
                    current_company['data']['logo_url'] = img['src']

                pills_items = main_box_flex_row_items[1].find_all(recursive=False)
                pills2 = list(sorted([x.text for x in pills_items[1].find_all('span')])) if len(
                    pills_items) >= 2 else []
                pills3 = list(sorted([x.text for x in pills_items[2].find_all('span')])) if len(
                    pills_items) >= 3 else []
                current_company['data']['pills'] = {
                    'orange': pills_items[0].text if len(pills_items) >= 1 else []
                }
                if len(pills_items) == 2:
                    current_company['data']['pills']['others'] = pills2
                elif len(pills_items) == 3:
                    current_company['data']['pills']['industries'] = pills2
                    current_company['data']['pills']['others'] = pills3

                if h1 := main_box_items[1].find('h1'):
                    current_company['data']['name'] = h1.text
                if h3 := main_box_items[1].find('h3'):
                    current_company['data']['headline'] = h3.text
                if p := main_box_items[1].find('p', class_='pre-line'):
                    current_company['data']['description'] = p.text
                if div := main_box_items[1].find('div', class_='links'):
                    current_company['data']['links'] = list(sorted([x['href'] for x in div.find_all('a')]))

                if highlight_box := section.find('div', class_='highlight-box'):
                    if div := highlight_box.find('div', class_='facts'):
                        current_company['data']['facts'] = {x.find(text=True, recursive=False): x.find('span').text for
                                                            x in
                                                            div.find_all('div')}
                    if div := highlight_box.find('div', class_='social-links'):
                        current_company['data']['social_links'] = extract_social_links(div)
            elif aside == 'Active Founders':
                current_company['data']['active_founders'] = extract_founders(section)
            elif aside == 'Former Founders':
                current_company['data']['former_founders'] = extract_founders(section)
            elif aside == 'Open Jobs':
                if job_openings := section.find('table', class_='job-openings'):
                    current_company['data']['jobs'] = [{
                        'title': x.find('td', class_='job-title').text,
                        'location': x.find('td', class_='job-location').text,
                        'apply': x.find('td', class_='job-apply').find('a')['href']
                    } for x in job_openings.find_all('tr')]

        with deps.MONGO.start_session() as session, session.start_transaction():
            previous_company = deps.MONGO_DB['company_snapshots'].find_one({
                '$query': {'id': company_id},
                '$orderby': {'$natural': -1}
            }, session=session) or {}
            previous_company.pop('_id', None)

            if previous_company != current_company:
                diff.send(diff.COMPANY, previous_company, current_company, include_current=True)

                deps.MONGO_DB['company_snapshots'].insert_one(current_company, session=session)


def extract_social_links(element):
    return {x['class'][1]: x['href'] for x in element.find_all('a')}


def extract_founders(element):
    if (founders_info := element.find_all('div', class_='founder-info')) and len(founders_info) > 0:
        return list(sorted([{
            'name': x.find('h3').text,
            'description': x.find('p', class_='pre-line').text,
            'thumb_url': x.find('img')['src'],
            'social_links': extract_social_links(x.find('div', class_='social-links'))
        } for x in founders_info], key=lambda x: x['name']))
    else:
        return []
