import requests
import urllib3
import urllib
import hmac
import hashlib
import json
import pprint
import pandas as pd
import numpy as np
from itertools import count
import time
import poloniex

## capture and calculation functions
def capture():
    url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=all&depth=10'
    try:
        response1 = requests.get(url)
    except requests.exceptions.Timeout:
        time.sleep(15)
        response1 = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    data = response1.json()
    df = pd.DataFrame(data)
    return df

def wtd_bid(pair, df):
    raw_bids = pd.DataFrame(df[pair]['bids'][0:2], columns=['price','volume'])
    raw_bids['price'] = pd.to_numeric(raw_bids['price'])
    raw_bids['volume'] = pd.to_numeric(raw_bids['volume'])
    wtd_bid = np.average(raw_bids['price'], weights=raw_bids['volume'])
    wtd_bid_vol = raw_bids['volume'].sum()
    return(wtd_bid, wtd_bid_vol)

def wtd_ask(pair, df):
    raw_asks = pd.DataFrame(df[pair]['asks'][0:2], columns=['price','volume'])
    raw_asks['price'] = pd.to_numeric(raw_asks['price'])
    raw_asks['volume'] = pd.to_numeric(raw_asks['volume'])
    wtd_ask = np.average(raw_asks['price'], weights=raw_asks['volume'])
    wtd_ask_vol = raw_asks['volume'].sum()
    return(wtd_ask, wtd_ask_vol)

def wtd(pair, df):
    return pd.DataFrame([wtd_bid(pair, df),wtd_ask(pair, df)], index=['BID','ASK'], columns=[pair, 'Volume'])



#BCH = capture('BTC_BCH')



#     if(command == "returnTicker" or command == "return24Volume"):
#         ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
#         return json.loads(ret.read())
#     elif(command == "returnOrderBook"):
#         ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
#         return json.loads(ret.read())
#     elif(command == "returnMarketTradeHistory"):
#         ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
#         return json.loads(ret.read())
#     elif(command == "returnChartData"):
#         ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=returnChartData&currencyPair=' + str(req['currencyPair']) + '&start=' + str(req['start']) + '&end=' + str(req['end']) + '&period=' + str(req['period'])))
#         return json.loads(ret.read())
#     else:

#





##setup trade information

API_ENDPOINT = 'https://poloniex.com/tradingApi'
APIKEY = 'MKZO419B-OCO54O0N-HSMJONT7-1N0YBR0N'
SECRET = 'e08c3b59680c42f2e422c4386042d26b73e979c4a049db27ecf92359cbee89b9ae9f0c78c8fc040b5162c548c7ea6d0beeb016f2fc5e601ee315f3c8bad10ac6'

polo = poloniex.Poloniex(APIKEY, SECRET)

triplets_test = [['USDT_XMR', 'BTC_XMR', 'USDT_BTC']]
# for tick, i in triplets_test:
#     pologet = polo.returnTicker()
#     print(f'{tick} :: {pologet[tick]}')


balance_list = ['BTC','DASH','LSK','STR','XMR','XRP','ZRX', 'USDT']
for tick in balance_list:
    polo_bal = polo.returnBalances()
    print(f'{tick} balance ::: {polo_bal[tick]}')

df = capture()

def trade_result(results):
    trades = [val.get('amount') for val in results['resultingTrades']]
    units = sum([float(i) for i in trades])
    print(f'Transacted {units} units')
    return units

def trade(df):
    for triplet in triplets_test:
        amt1 = 10/wtd(triplet[0], df).loc['ASK'][triplet[0]]
        print(amt1)
        results1 = polo.buy(currencyPair=triplet[0], rate=wtd(triplet[0], df).loc['ASK'][triplet[0]], amount=amt1)
        amt2 = trade_result(results1) * wtd(triplet[1], df).loc['BID'][triplet[1]]
        print(amt2, results1)
        results2 = polo.sell(currencyPair=triplet[1], rate=wtd(triplet[1], df).loc['BID'][triplet[1]], amount=amt2)
        amt3 = trade_result(results2) * wtd(triplet[2], df).loc['BID'][triplet[2]]
        print(amt3, results2)
        USDT = polo.sell(currencyPair=triplet[2], rate=wtd(triplet[2], df).loc['BID'][triplet[2]], amount=amt3)
        print(USDT)

        print(f'Round trip result is ${trade_result(USDT)}')


#tick = polo.returnTicker()
#print(tick['BTC_XRP'])

trade(df)

#balance = polo.returnBalances()
#amount = balance['BTC']
#print(f'I have {amount} BTC!')

# triplets_test = [['USDT_XMR', 'BTC_XMR', 'USDT_BTC']]
#
# results1 = polo.buy(currencyPair='BTC_XRP', rate=0.00137, amount=10)

#

#     if USDT > 1000:
#         print([USDT, triplet, time_1])
#         with open('log.csv', 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([[USDT, triplet, time_1]])
