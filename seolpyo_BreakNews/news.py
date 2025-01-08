from datetime import datetime
from html import unescape
import json
from pathlib import Path
import re
from time import sleep
from traceback import format_exc

from dateutil.parser import parse
import requests


from message import send, err


path_auth = Path(__file__).parent / 'secret n.txt'
with open(path_auth, 'r', encoding='utf-8') as txt: auth = json.load(txt)


session = requests.session()
session.headers = {
    'X-Naver-Client-Id': auth['id'],
    'X-Naver-Client-Secret': auth['secret']
}

url = 'https://openapi.naver.com/v1/search/news.json'
payload = {
    'query': '속보',
    'display': 100,
    'start': 1,
    'sort': 'date',
}


def main():
    dict_word = {}
    dict_word_past = {}
    for i in range(10):
        if i: sleep(0.11)
        try: news_list = search(i * 100 + 1)
        except:
            msg = format_exc()
            raise
        Break, word_dict, past_word_dict = get_word(news_list)
        for k in word_dict:
            try: dict_word[k]
            except: dict_word[k] = []
            dict_word[k] += word_dict[k][0] + word_dict[k][1]

        for k in past_word_dict:
            try: dict_word_past[k]
            except: dict_word_past[k] = 0
            dict_word_past[k] += len(past_word_dict[k])
        if Break: break

    word_list = []
    # print('\ndict_word')
    for word, list_news in dict_word.items():
        # print(f'{word=}')
        length = len(list_news)
        # print(f'{length=}')
        if length < 6: continue

        try: dict_word_past[word]
        except: continue
        if 5 < dict_word_past[word]: continue

        news = list_news[0]
        word_list.append((word, length, news))

    # print('\ndict_word_past')
    # for word, length in dict_word_past.items():
    #     print(f'{word=}')
    #     print(f'{length=}')

    list_word, set_link = ([], set())
    for i in sorted(word_list, key=lambda x: x[1]):
        if i[2] not in set_link:
            list_word.append(i)
            set_link.add(i[2])

    len_list = list_word.__len__()
    for n, (word, length, news) in enumerate(list_word, 1):
        # print(f"{(word, length, news['title'])=}")
        msg = f"""{n:,}/{len_list:,}. {length:,}회, [{word}]\n<a href="{news['link']}">{news['title']}</a>"""
        send(msg)
    return


def search(start=1) -> list[dict[str, str]]:
    payload['start'] = start

    with session.get(url, params=payload, timeout=5) as r:
        r.raise_for_status()
        j: dict = r.json()

    return j['items']


def get_word(news_list: list[dict[str, str]]):
    ten, fifteen, end_second = (60 * 10, 60 * 15, 60 * 25)
    now = parse(datetime.now().__str__() + '+0900')
    # print(f'{now=}')

    dict_word: dict[str, list[list[dict]]] = {}
    dict_word_past: dict[str, list[dict]] = {}
    boolen = False
    for news in news_list:
        # print(f"{news['pubDate']=}")
        date = parse(news['pubDate'])
        # print(f'{date=}')
        seconds = (now - date).seconds
        # print(f'{seconds=}')
        if end_second < seconds:
            boolen = True
            break

        title = news['title'].replace('<b>', '').replace('</b>', '')
        if '속보' not in title: continue

        title = unescape(title)
        if title.endswith('...'): title = title[:-3]
        title = ''.join(title.split())
        for i in "‘’": title = title.replace(i, "'")
        for i in '“”': title = title.replace(i, '"')

        word_list1 = re.findall('"(.+?)"', title)

        word_list2 = re.findall("'(.+?)'", title)

        word_list3 = re.findall(r""".*\.\.([^'"]+?)['"]""", title)

        word_list4 = re.findall(r"""…([^'"]+?)['"]""", title)

        set_word = {i for i in word_list1+word_list2+word_list3+word_list4}
        # print(f'{(title, set_word)=}')
        if seconds <= fifteen:
            for word in set_word:
                if word:
                    try: dict_word[word]
                    except: dict_word[word] = [[], []]
                    if 'news.naver.com' in news['link']: dict_word[word][0].append(news)
                    else: dict_word[word][1].append(news)
        if ten < seconds:
            for word in set_word:
                if word:
                    try: dict_word_past[word]
                    except: dict_word_past[word] = [[], []]
                    dict_word_past[word].append(news)

    return (boolen, dict_word, dict_word_past)


if __name__ == '__main__':
    # search(10)
    try: main()
    except:
        e = format_exc()
        err(e)

