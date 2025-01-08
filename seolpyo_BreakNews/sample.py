import json
from pathlib import Path
from pprint import pprint

import requests


path_auth = Path(__file__).parent / 'secret n.txt'
with open(path_auth, 'r', encoding='utf-8') as txt: auth = json.load(txt)


session = requests.session()
session.headers = {
    'X-Naver-Client-Id': auth['id'],
    'X-Naver-Client-Secret': auth['secret']
}

url = 'https://openapi.naver.com/v1/search/news.json'
payload = {
    'query': '속보 공휴일',
    'display': 10,
    'start': 1,
    'sort': 'date',
}

with session.get(url, params=payload, timeout=5) as r:
    j: dict = r.json()

for i in enumerate(j['items']): pprint(i, sort_dicts=False)



