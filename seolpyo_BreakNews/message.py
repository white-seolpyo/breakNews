import json
from pathlib import Path
from time import sleep

import telepot


path = Path(__file__).parent / 'secret tg.txt'
with open(path, 'r', encoding='utf-8') as txt:
    secret = json.loads(txt.read())
bot = telepot.Bot(secret['token'])


def send(text):
    try: bot.sendMessage(secret['breaknews'], text=text, disable_web_page_preview=True, parse_mode='html')
    except telepot.exception.TooManyRequestsError as e:
        # print(f'{e.json=}')
        time_sleep = e.json['parameters']['retry_after'] + 1
        # print(f'{time_sleep=}')
        sleep(time_sleep)
        bot.sendMessage(secret['breaknews'], text=text, disable_web_page_preview=True, parse_mode='html')
    return


def err(text):
    bot.sendMessage(secret['master'], text=text, disable_web_page_preview=True, parse_mode=None)
    return


if __name__ == '__main__':
    text = 'test message\n<a href="https://white.seolpyo.com/">하얀설표 블로그 바로가기</a>'
    send(text)
    err(text)