import urllib
import urllib3
import certifi
import json
import requests
import pprint
import time
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import csv

triplets1 = [['USDT_XMR', 'BTC_XMR', 'USDT_BTC'],['USDT_ETC', 'BTC_ETC', 'USDT_BTC'],['USDT_ETH', 'BTC_ETH', 'USDT_BTC'],['USDT_LTC', 'BTC_LTC', 'USDT_BTC']]
triplets2 = [['USDT_BTC', 'BTC_ETH', 'USDT_ETH'],['USDT_BTC', 'BTC_LTC', 'USDT_LTC'],['USDT_BTC', 'BTC_XRP', 'USDT_XRP']]
triplets3 = [['BTC_ETH', 'ETH_BCH', 'BTC_BCH']]
triplets4 = [['XMR_LTC', 'BTC_LTC', 'BTC_XMR']]

def wtd_bid(pair, df):
    raw_bids = pd.DataFrame(df[pair]['bids'][0:3], columns=['price','volume'])
    raw_bids['price'] = pd.to_numeric(raw_bids['price'])
    raw_bids['volume'] = pd.to_numeric(raw_bids['volume'])
    wtd_bid = np.average(raw_bids['price'], weights=raw_bids['volume'])
    wtd_bid_vol = raw_bids['volume'].sum()
    return(wtd_bid, wtd_bid_vol)

def wtd_ask(pair, df):
    raw_asks = pd.DataFrame(df[pair]['asks'][0:3], columns=['price','volume'])
    raw_asks['price'] = pd.to_numeric(raw_asks['price'])
    raw_asks['volume'] = pd.to_numeric(raw_asks['volume'])
    wtd_ask = np.average(raw_asks['price'], weights=raw_asks['volume'])
    wtd_ask_vol = raw_asks['volume'].sum()
    return(wtd_ask, wtd_ask_vol)

def wtd(pair, df):
    return pd.DataFrame([wtd_bid(pair, df),wtd_ask(pair, df)], index=['BID','ASK'], columns=[pair, 'Volume'])


def capture():
    url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=all&depth=10'
    try:
        response1 = requests.get(url)
    except requests.exceptions.Timeout:
        time.sleep(120)
        response1 = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    dict = response1.json()
    df = pd.DataFrame(dict)
    return df

def analyze(time_1, df):
    """
    start with $1000, buy denom at ask - minus commission
    take second currency and buy numerator at bid - minus commission
    take third currency and buy numerator at bid - minus commission
    --reverse middle step when middle pair is reversed (triplets2)
    """

    for triplet in triplets1:
        step1 = 1000 / wtd(triplet[0], df).loc['ASK'][triplet[0]]*.9985
        step2 = step1 * wtd(triplet[1], df).loc['BID'][triplet[1]]*.9985
        USDT = step2 * wtd(triplet[2], df).loc['BID'][triplet[2]]*.9985

        if USDT > 1000:
            print([USDT, triplet, time_1])
            with open('log.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([[USDT, triplet, time_1]])


    for triplet in triplets2:
        step1 = 1000 / wtd(triplet[0], df).loc['ASK'][triplet[0]]*.9985
        step2 = step1 / wtd(triplet[1], df).loc['ASK'][triplet[1]]*.9985
        USDT = step2 * wtd(triplet[2], df).loc['BID'][triplet[2]]*.9985

        if USDT > 1000:
            print([USDT, triplet, time_1])
            with open('log.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([[USDT, triplet, time_1]])

    for triplet in triplets3:
        step1 = .1 / wtd(triplet[0], df).loc['ASK'][triplet[0]]*.9985
        step2 = step1 / wtd(triplet[1], df).loc['ASK'][triplet[1]]*.9985
        BTC = step2 * wtd(triplet[2], df).loc['BID'][triplet[2]]*.9985

        if BTC > .1:
            print([BTC, triplet, time_1])
            with open('log.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([[BTC, triplet, time_1]])

    for triplet in triplets4:
        step1 = 10 * wtd(triplet[0], df).loc['BID'][triplet[0]]*.9985
        step2 = step1 / wtd(triplet[1], df).loc['ASK'][triplet[1]]*.9985
        XMR = step2 * wtd(triplet[2], df).loc['BID'][triplet[2]]*.9985

        if XMR > 10:
            print([XMR, triplet, time_1])
            with open('log.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([[XMR, triplet, time_1]])

def execute_go():
    time_1 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    time_1
    df = capture()
    analyze(time_1, df)


while True:
    execute_go()
    time.sleep(20)

if __name__ == "__main__":
    main()
