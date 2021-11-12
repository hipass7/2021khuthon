# -*- coding: utf-8 -*-
import requests
import time
from datetime import datetime, timedelta
import ccxt
import json
import util

# +
import json
import logging
import requests
from bs4 import BeautifulSoup
import re
import time

request_header = {
    "Accept": "*/*",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}
# -








def get_user_list():
    res = requests.get("http://localhost:8000/trading/userlist/")
    return json.loads(res.text)


def check_mode():
    users_info = get_user_list()

    for user in users_info:
        if user['is_trading']:
            yield user


while True:
    symbol = "ETH/USDT"
    binance = ccxt.binance()
    long_target, short_target, ma20_condition, before_day_condition = util.cal_target(binance, symbol)
    eth = binance.fetch_ticker(symbol=symbol)
    cur_price = eth['last']
    is_trading_start = False

    now = datetime.now()
    start = now.replace(hour=9, minute=0, second=20)
    end = now.replace(hour=8, minute=55, second=40)

    if now.hour == 9 and now.minute == 0 and (10 <= now.second < 20): # 타겟 가격 갱신
        long_target, short_target, ma20_condition, before_day_condition = util.cal_target(binance, symbol)
        time.sleep(10)

    trading_user_info_list = []
    for user in check_mode():
        user_dict = dict()
        user_dict['user'] = user
        user_binance = ccxt.binance(config={
            'apiKey': user['api_key'],
            'secret': user['secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }})

        balance = user_binance.fetch_balance()
        usdt = balance['total']['USDT']
        user_dict['binance'] = user_binance
        user_dict['usdt_balance'] = usdt
        user_dict['op_mode'] = False
        user_dict['position'] = {"type": None, "amount": 0}

        if short_target <= cur_price <= long_target:
            user_dict['op_mode'] = True

        trading_user_info_list.append(user_dict)

    while (now > start or now < end):
        now = datetime.now()

        # position 종료
        if now.hour == 8 and now.minute == 55 and (20 <= now.second < 40):
            for user in trading_user_info_list:
                if user['op_mode'] and user['position']['type'] is not None:
                    order = util.exit_position(user['binance'], symbol, user['position'])
                    order['username'] = user['username']
                    order['target'] = {"long_target": long_target, "short_target": short_target}
                    requests.post("http://localhost:8000/trading/record/new", json=order[0])

                    user['op_mode'] = False
                    user['position']['type'] = None

            break  # 트레이딩 while 문 종료

        # 현재가, 구매 가능 수량
        eth = binance.fetch_ticker(symbol=symbol)
        cur_price = eth['last']

        for user in trading_user_info_list:
            user['amount'] = util.cal_amount(user['usdt_balance'], cur_price, 0.95)

            if user['op_mode'] and user['position']['type'] is None:
                user['position']['type'], user['invest_amount'], order = util.enter_position(user['binance'], symbol, cur_price,
                                                                                      long_target, short_target,
                                                                                      user['amount'], user['position'], ma20_condition,
                                                                                      before_day_condition)

                if user['position']['type']:
                    order['target'] = {"long_target": long_target, "short_target": short_target}
                    requests.post("http://localhost:8000/trading/record/new", json=order[0])
                    order['username'] = user['username']

        time.sleep(0.5)

