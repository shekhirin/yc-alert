import urlpath


def generate_twitter(company) -> str:
    by_twitter = by([f'@{urlpath.URL(z).parts[1]}' for x in company['data']['founders'] for y, z in
                     x['social_links'].items() if y == 'twitter'])

    return (
        f'{company["data"]["name"]}{by_twitter} has just been added to {company["batch"]} batch<br><br>'
        f'More info: https://www.ycombinator.com/companies/{company["id"]}'
    )


def generate_telegram(company) -> str:
    by_telegram = by([f'<a href="{z}">@{urlpath.URL(z).parts[1]}</a>' for x in company['data']['founders']
                      for y, z in x['social_links'].items() if y == 'twitter'])

    return (
        f'<a href="{company["data"]["links"][0]}">{company["data"]["name"]}</a>{by_telegram} '
        f'has just been added to {company["batch"]} batch<br><br>'
        f'More info: https://www.ycombinator.com/companies/{company["id"]}'
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
