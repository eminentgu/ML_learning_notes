#!/usr/bin/python
# -*- coding: utf-8 -*-

# OKX 欧易
# https://www.okx.com

import base64
import copy
import datetime
import hmac
import json
import math
import sys
import time
import urllib.parse

import numpy as np
import requests


class OKXV5():

    _api_url = "https://www.okx.com"
    _ws_url = ""

    #初始化
    def __init__(self, apikey="", secret="", phrase=""):
        self._apikey = apikey
        self._secret = secret
        self._phrase = phrase

    # 币种列表
    def coins(self):
        result = self.symbols()
        coins = [] #所有币种
        for key, values in result.items():
            if values['base'] not in coins:
                coins.append(values['base'])
        return coins

    # 交易对，包含markets and precisions
    def symbols(self, market='SPOT'):
        params = {
            'instType' : market
        }
        url = self._api_url + '/api/v5/public/instruments' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        # print(result)
        dict = {}
        feelevel = {"1":0.001,  "2":0.0006, "3":0.001, "4":0.0} #Lv1 taker 吃单
        # feelevel  = {"1":0.0, "2":0.0, "3":0.0, "4":0.0} #0手续费 用于测试
        for item in result['data']:
            if market in ["SWAP"]:
                symbol = item["instId"]
            else:
                symbol = item["baseCcy"] + "_" + item["quoteCcy"]

            filter_dict = {}
            filter_dict['symbol'] = item["instId"]  #原始symbol
            filter_dict['type'] = item["instType"]
            filter_dict['price'] = abs(round(math.log(float(item["tickSz"]), 10)))
            filter_dict['quantity'] = abs(round(math.log(float(item["lotSz"]), 10)))
            filter_dict['min'] = float(item["minSz"])
            filter_dict['fee'] = float(feelevel[item["category"]])
            filter_dict['feelevel'] = int(item["category"])
            if market in ["SWAP", "MARGIN"]:
                filter_dict['lever'] = int(item["lever"])
            # print(symbol)
            if market in ["SPOT"]:
                filter_dict['base'] = item["baseCcy"]
                filter_dict['quote'] = item["quoteCcy"]
            if market in ["SWAP"]:
                filter_dict['ctval'] = item["ctVal"]
                filter_dict['ctmult'] = item["ctMult"]
                filter_dict['cttype'] = item["ctType"]
                filter_dict['ctvalccy'] = item["ctValCcy"]
                filter_dict['quantity'] = item["lotSz"]
            # print(item)
            # print(filter_dict)
            dict[symbol] = filter_dict
        return dict
    def _x_symbol(symbol,temp):
        print('helphelp',temp)
        return temp
    # 行情
    def ticker(self, symbol='BTC_USDT'):
        params =  {
            'instId':self._x_symbol(symbol)
        }
        url = self._api_url + '/api/v5/market/ticker' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        dict = {'bid': float(result['data'][0]["bidPx"]), 'ask': float(result['data'][0]["askPx"]), 'last': float(result['data'][0]["last"]), 'high':float(result['data'][0]["high24h"]), 'low':float(result['data'][0]["low24h"])}
        return dict

    # 所有行情
    def tickers(self, market='SPOT'):
        params = {
            'instType' : market
        }
        url = self._api_url + '/api/v5/market/tickers' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        # print(result)
        ticker_dict = {}
        if 'data' not in result:
            return None

        for item in result['data']:
            symbol = item["instId"].replace("-", "_")
            if market in ["SWAP", "MARGIN"]:
                symbol = item["instId"]

            try:
                if item["askPx"] == '' or item["askSz"] == '' or item["bidPx"] == '' or item["bidSz"] == '' or item["ts"] == '':
                    continue
                ticker_dict[symbol] = {'ask': {'price': float(item["askPx"]), 'quantity': float(item["askSz"])},
                                       'bid': {'price': float(item["bidPx"]), 'quantity': float(item["bidSz"])},
                                       'last': float(item["last"]),
                                       'ts': int(item["ts"])}
                if market in ["SWAP", "MARGIN"]:
                    ticker_dict[symbol]['vol24h'] = float(item["vol24h"])
            except Exception as e:
                print([symbol, item, repr(e)])
        return ticker_dict

    # 深度
    def depth(self, symbol = 'BTC_USDT', limit = 30):
        params = {
            'instId': self._x_symbol(symbol),
            'sz' : limit
        }
        url = self._api_url + '/api/v5/market/books' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        data = result['data'][0]
        dict = {}
        bids, asks = [], []
        for i in range(min(len(data["bids"]),len(data["asks"]), limit)):
            bids.append(list(map(float, [data["bids"][i][0], data["bids"][i][1]])))
            asks.append(list(map(float, [data["asks"][i][0], data["asks"][i][1]])))
        dict = {'asks': asks, 'bids': bids}
        return dict

    # 获取交易信息(60条)
    def trades(self, symbol = 'BTC_USDT', limit = 60):
        params = {
            'instId': self._x_symbol(symbol),
            'limit': limit
        }
        url = self._api_url + '/api/v5/market/trades' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        list = []
        for item in result['data']:
            list.append({'orderid': item["tradeId"], 'time': int(item["ts"]), 'price': float(item["px"]), 'quantity': float(item["sz"]), 'side': item["side"].upper()})
        return list

    # k线
    def kline(self, symbol = 'BTC_USDT', interval = '1hour', limit = 120, start = None, end = None):
        xdict = {
            "1min":"1m",
            "3min":"3m",
            "5min":"5m",
            "10min":"",
            "15min":"15m",
            "30min":"30m",
            "1hour":"1H",
            "2hour":"2H",
            "3hour":"",
            "4hour":"4H",
            "6hour":"6H",
            "8hour":"",
            "12hour":"12H",
            "1day":"1D",
            "3day":"",
            "1week":"1W",
            "2week":"",
            "1month":"1M"
        }
        if not xdict[interval]:
            print('不支持的K线周期 %s not support %s'%(self._exchange, interval))
            return None

        params = {
            'instId': self._x_symbol(symbol),
            'bar' : xdict[interval],
            'limit': limit
        }

        if start:
            params["before"] = '%s000'%(start)
        if end:
            params["after"] = '%s000'%(end)

        url = self._api_url + '/api/v5/market/candles' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url, headers=self.header(self.signature()))
        # print(result)
        time.sleep(0.2) #限速： OKEX  20次/2s
        # if (len(result['data']) < 60): #分析最小要求 60
            # self._x_print(symbol, sys._getframe().f_code.co_name, interval + " 数组维度过小" + str(len(data)))

        stamp, open, high, low, close, volume = [], [], [], [], [], []
        for index in range(len(result['data']) - 1, -1, -1):
            stamp.append(int(float(result['data'][index][0]) / 1000))
            open.append(float(result['data'][index][1]))
            high.append(float(result['data'][index][2]))
            low.append(float(result['data'][index][3]))
            close.append(float(result['data'][index][4]))
            volume.append(float(result['data'][index][6]))

        return np.array(stamp), np.array(open), np.array(high), np.array(low), np.array(close), np.array(volume)

    # k线
    def kline_history(self, symbol = 'BTC_USDT', interval = '1hour', limit = 120, start = None, end = None):
        xdict = {
            "1min":"1m",
            "3min":"3m",
            "5min":"5m",
            "10min":"",
            "15min":"15m",
            "30min":"30m",
            "1hour":"1H",
            "2hour":"2H",
            "3hour":"",
            "4hour":"4H",
            "6hour":"6H",
            "8hour":"",
            "12hour":"12H",
            "1day":"1D",
            "3day":"",
            "1week":"1W",
            "2week":"",
            "1month":"1M"
        }
        if not xdict[interval]:
            print('不支持的K线周期 %s not support %s'%(self._exchange, interval))
            return None

        params = {
            'instId': self._x_symbol(symbol),
            'bar' : xdict[interval],
            'limit': limit
        }

        if start:
            params["before"] = start
        if end:
            params["after"] = end

        url = self._api_url + '/api/v5/market/history-candles' + "?" + urllib.parse.urlencode(params)
        result = self.http_request_v2(url)

        if (len(result['data']) < 60): #分析最小要求 60
            #self._x_print(symbol, sys._getframe().f_code.co_name, interval + " 数组维度过小" + str(len(data)))
            self._x_print(symbol, sys._getframe().f_code.co_name, interval + " 数组维度过小" + str(result['data']))

        stamp, open, high, low, close, volume = [], [], [], [], [], []
        for index in range(len(result['data']) - 1, -1, -1):
            stamp.append(float(result['data'][index][0]) / 1000)
            open.append(float(result['data'][index][1]))
            high.append(float(result['data'][index][2]))
            low.append(float(result['data'][index][3]))
            close.append(float(result['data'][index][4]))
            volume.append(float(result['data'][index][6]))

        return np.array(stamp), np.array(open), np.array(high), np.array(low), np.array(close), np.array(volume)

    # 账号
    def account(self):
        body = {}
        path = '/api/v5/account/balance'
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))
        # print(result)
        if int(result['code']) != 0:
            print(result)
            return result

        dict = {}
        for item in result['data'][0]["details"]:
            free = item["availBal"] if (item["availBal"] != '') else item["availEq"]
            # if market in ['SPOT']: #现货
                # dict[item["ccy"]] = {'free':float(item["availBal"]), 'locked':float(item["frozenBal"]), "total":float(item["cashBal"]), "usd":float(item["eqUsd"])}
            # elif market in ['SWAP', 'MARGIN']:  #杠杆, 永续，交割
                # dict[item["ccy"]] = {'free':float(item["availEq"]), 'locked':float(item["frozenBal"]), "total":float(item["cashBal"]), "usd":float(item["eqUsd"])}
            dict[item["ccy"]] = {'free':float(free), 'locked':float(item["frozenBal"]), "total":float(item["eq"]), "usd":float(item["eqUsd"])}
        return dict


    # 查看账户配置
    def account_config(self):
        body = {}

        path = '/api/v5/account/config'
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))
        return result['data']

    # 设置杠杆倍数
    def account_leverage(self, symbol, lever, mode="ISOLATED"):
        if mode not in ["ISOLATED", "CROSS"]:
            raise Exception("ERROR params mode %s "%(mode))
            return

        path = '/api/v5/account/set-leverage'
        url = self._api_url + path
        body = {
            'instId'    :self._x_symbol(symbol),
            'lever'     :lever,
            'mgnMode'   :mode.lower(),
        }
        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))
        time.sleep(0.1)
        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['code'], 'errmsg': result['msg']}
        else:
            return {'result': True, 'symbol': symbol, 'lever': result['data'][0]['lever'], 'mode': result['data'][0]['mgnMode']}

    # 下订单
    def order(self, symbol, side, type, quantity=None, price=None, mode="CASH", posside=None, **kwargs):
        if side not in ["BUY", "SELL"] or type not in ["MARKET","LIMIT","POST_ONLY","FOK","IOC","OPTIMAL_LIMIT_IOC"]:
            raise Exception("ERROR params side %s type %s"%(side, type))
            return

        if mode not in ["ISOLATED", "CROSS", "CASH"]:
            raise Exception("ERROR params mode %s"%(mode))
            return

        #科学计数法转为字符串提交
        if 'e-' in str(price) :
            price = '%.20f'%(price)

        if 'e-' in str(quantity) :
            quantity = '%.20f'%(quantity)

        path = '/api/v5/trade/order'
        url = self._api_url + path
        body = {
            'instId'    :self._x_symbol(symbol),
            'tdMode'    :mode.lower(),
            'side'      :side.lower(),
            'ordType'   :type.lower(),
            'px'        :price,
            'sz'        :quantity
        }

        #  sz 当币币/币币杠杆以市价买入时，指计价货币的数量
        if side in ["BUY"] and type in ["MARKET"]:    #市价买单不传price
            body.pop('px')
            body['sz'] = price
        if posside:
            body['posSide'] = posside.lower()
        for key, value in kwargs.items():
            body[key] = value
        print(body)
        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))

        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['data'][0]['sCode'], 'errmsg': result['data'][0]['sMsg']}
        else:
            return {'result': True, 'orderid': result['data'][0]['ordId']}

    # 订单取消
    def order_cancel(self, symbol, orderid):
        body = {
            'instId': self._x_symbol(symbol),
            'ordId' : orderid
        }
        path = '/api/v5/trade/cancel-order'

        url = self._api_url + path
        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))
        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['data'][0]['sCode'], 'errmsg': result['data'][0]['sMsg']}
        else:
            return {'result': True}

    # 订单查询
    def order_query(self, symbol, orderid):
        body = {
            'instId': self._x_symbol(symbol),
            'ordId' : orderid
        }
        path = '/api/v5/trade/order' + "?" + urllib.parse.urlencode(body)
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))
        types = {
            "live":"SUBMITTED",
            "partially_filled":"PARTIALLY_FILLED",
            "filled":"FILLED",
            "canceled":"CANCELED",
        }
        if int(result['code']) == 0:
            dict = {
            'symbol':   symbol,
            'trade':    result["data"][0]["instType"],
            'level':    result["data"][0]["lever"],
            'mode':     result["data"][0]["tdMode"].upper(),
            'orderid':  result["data"][0]["ordId"],
            'price':    float(result["data"][0]["avgPx"]) if result["data"][0]["avgPx"] else float(result["data"][0]["px"]),
            'quantity': float(result["data"][0]["sz"]),
            'status':   types[result["data"][0]["state"]],
            'type':     result["data"][0]["ordType"].upper(),
            'side':     result["data"][0]["side"].upper(),
            'time':     result["data"][0]["cTime"],
            }
            return dict
        else:
            return {'result': False, 'errcode': result['code'], 'errmsg': result['msg']}

    # 未成交订单
    def order_open(self,  symbol=None, market='SPOT',  **kwargs):
        body = {
            'instType': market
        }
        if symbol:
           body['instId'] = self._x_symbol(symbol)

        for key, value in kwargs.items():
            body[key] = value
        path = '/api/v5/trade/orders-pending' + "?" + urllib.parse.urlencode(body)
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))
        list = []
        for item in result["data"]:
            # print(item)
            list.append({'symbol': item["instId"], 'trade': item["instType"], 'level': item["lever"], 'mode':item["tdMode"], 'orderid': item["ordId"], 'time': int(item["cTime"]), 'price': float(item["px"]), 'quantity': float(item["sz"]), 'side': item["side"].upper(), 'type': item["ordType"].upper()})


        if len(result["data"]) > 1:
            # print(len(result["data"])) #未生效
            list.extend(self.order_open(after = result["data"][-1]["ordId"]))
        return list

    # 历史订单（已成交）（7/30天）
    def order_history(self, symbol=None, instType='SPOT', **kwargs):
        params = {
            'instType': instType,
        }
        if symbol:
           params['instId'] = self._x_symbol(symbol)
        for key, value in kwargs.items():
            params[key] = value
        print(params)
        path = '/api/v5/trade/orders-history' + "?" + urllib.parse.urlencode(params) #7天
        # path = '/api/v5/trade/orders-history-archive' + "?" + urllib.parse.urlencode(params) #30天
        url = self._api_url + path
        params = self.signature("GET", path, params)
        result = self.http_request_v2(url, headers=self.header(params))
        types = {
            "live":"SUBMITTED",
            "partially_filled":"PARTIALLY_FILLED",
            "filled":"FILLED",
            "canceled":"CANCELED",
        }
        list = []
        for item in result["data"]:
            symbol = item["instId"].split("-")
            try:
                price = item["avgPx"] if item["avgPx"] != '' else item["px"]
                list.append({'orderid': item["ordId"], 'symbol':symbol[0] + "_" + symbol[1], 'time': int(item["uTime"]), 'price': float(price), 'quantity': float(item["sz"]), 'side': item["side"].upper(), 'type': item["ordType"].upper(), 'status':types[item["state"]]})
            except Exception as e:
                print([repr(e)])
                print(item)

        if len(result["data"]) > 1:
            print(len(result["data"]))
            list.extend(self.order_history(after = result["data"][-1]["ordId"]))

        return list

    # 查看持仓信息
    def positions(self, symbol=None, market=None):
        body = {}
        if market:
            body['instType'] = market
        if symbol:
            body['instId'] = self._x_symbol(symbol)
        if body:
            path = '/api/v5/account/positions' + "?" + urllib.parse.urlencode(body)
        else:
            path = '/api/v5/account/positions'
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))
        # print(result)
        list = []
        for item in result["data"]:
            # if float(item["pos"]) > 0.0:  #如果该instId拥有过的仓位，将返回持仓信息，不管持仓量是否为0；否则不返回
            list.append({'symbol': item["instId"], 'posid': item["posId"], 'tradeid': item["tradeId"], 'type': item["instType"], 'mode': item["mgnMode"].upper(), 'side': item["posSide"].upper(),'adl': item["adl"],'usd': item["notionalUsd"], 'avgprice': float(item["avgPx"]), 'pos': float(item["pos"]), 'upl': round(float(item["upl"]),4), 'uplratio': round(float(item["uplRatio"]),2), 'lever': int(item["lever"]), 'liqprice': item["liqPx"] if item["liqPx"] else 0, 'margin': item["margin"] if item["margin"] else item["imr"], 'mgnratio': round(float(item["mgnRatio"]), 2), 'mmr': item["mmr"], 'ccy': item["ccy"],'ctime': int(item["cTime"])})

        return list


    #市价仓位全平
    def position_close(self, symbol, side='NET', mode='ISOLATED', ccy=None):
        path = '/api/v5/trade/close-position'
        url = self._api_url + path

        body = {
            'instId' : self._x_symbol(symbol),
            'posSide' : side.lower(),
            'mgnMode': mode.lower(),
        }
        if ccy:
            body['ccy'] = ccy

        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))
        # print(result)

        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['code'], 'errmsg': result['msg']}
        else:
            return {'result': True, 'symbol': (result['data'][0]['instId']).replace("-","_")}

    # 策略委托下单   单向止盈止损委托 、双向止盈止损委托、计划委托、冰山委托、时间加权委托
    def order_algo(self, symbol, side, type, quantity=None, price=None, mode='CASH', **kwargs):
        if side not in ["BUY", "SELL"] or type not in ["CONDITIONAL", "OCO", "TRIGGER", "ICEBERG", "TWAP"]:
            raise Exception("ERROR params side %s type %s"%(side, type))
            return

        if mode not in ["ISOLATED", "CROSS", "CASH"]:
            raise Exception("ERROR params mode %s"%(mode))
            return

        path = '/api/v5/trade/order-algo'
        url = self._api_url + path
        body = {
            'instId'    :self._x_symbol(symbol),
            'tdMode'    :mode.lower(),
            'side'      :side.lower(),
            'ordType'   :type.lower(),
            'sz'        :quantity
        }

        for key, value in kwargs.items():
            body[key] = value
        # print(body)
        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))
        # print(result)
        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['data'][0]['sCode'], 'errmsg': result['data'][0]['sMsg']}
        else:
            return {'result': True, 'algoid': result['data'][0]['algoId']}

    # 策略委托订单撤销
    def order_algo_cancel(self, symbol, algoid, type="TRIGGER"):
        body = [{
            'instId': self._x_symbol(symbol),
            'algoId' : algoid
        }]
        if type in ["CONDITIONAL", "OCO", "TRIGGER"]:
            path = '/api/v5/trade/cancel-algos'
        elif type in ["ICEBERG", "TWAP"]:
            path = '/api/v5/trade/cancel-advance-algos'

        url = self._api_url + path
        params2 = self.signature("POST", path, body)
        result = self.http_request_v2(url, method='POST', headers=self.header(params2), params = json.dumps(body))
        if int(result['code']) != 0:
            return {'result': False, 'errcode': result['data'][0]['sCode'], 'errmsg': result['data'][0]['sMsg']}
        else:
            return {'result': True}

    # 策略委托订单查询
    def order_algo_query(self, symbol, algoid, type="TRIGGER"):
        body = {
            'instId': self._x_symbol(symbol),
            'algoId' : algoid,
            'ordType' : type.lower(),
        }
        path = '/api/v5/trade/orders-algo-history' + "?" + urllib.parse.urlencode(body)
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        result = self.http_request_v2(url, headers=self.header(params2))

        types = {
            "effective":"EFFECTIVE",
            "order_failed":"FAILED",
            "canceled":"CANCELED",
        }
        if int(result['code']) == 0:
            dict = {
                'symbol':   symbol,
                'algoid':  result["data"][0]["algoId"],
                'orderid':  result["data"][0]["ordId"],
                'tprice':    float(result["data"][0]["triggerPx"]),
                'price':    float(result["data"][0]["ordPx"]),
                'quantity': float(result["data"][0]["sz"]),
                'status':   types[result["data"][0]["state"]],
                'type':     result["data"][0]["ordType"].upper(),
                'side':     result["data"][0]["side"].upper(),
                'time':     result["data"][0]["cTime"],
            }
            return dict
        else:
            result2 = self.order_algo_open(symbol=symbol, algoid=algoid, type=type)
            return result2[0]

    # 策略委托未成交订单列表
    def order_algo_open(self, symbol=None, algoid=None, type="TRIGGER", itype=None):
        body = {
            'ordType' : type.lower()
        }
        if itype:
           body['instType'] = itype
        if symbol:
           body['instId'] = self._x_symbol(symbol)
        if algoid:
           body['algoId'] = algoid

        path = '/api/v5/trade/orders-algo-pending' + "?" + urllib.parse.urlencode(body)
        url = self._api_url + path
        params2 = self.signature("GET", path, body)
        time.sleep(0.1) #限速： OKEX  20次/2s
        result = self.http_request_v2(url, headers=self.header(params2))
        # print(result)
        list = []
        for item in result["data"]:
            list.append({'symbol': item["instId"].replace("-","_"), 'algoid': item["algoId"], 'orderid': item["ordId"], 'time': int(item["cTime"]), 'ordPx': item["ordPx"], 'triggerPx': item["triggerPx"], 'slTriggerPx': item["slTriggerPx"], 'quantity': float(item["sz"]), 'side': item["side"].upper(), 'type': item["ordType"].upper(), 'status': "SUBMITTED"})
        return list

    # 生成headers头
    def header(self, params=None):
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['OK-ACCESS-KEY'] = self._apikey
        headers['OK-ACCESS-SIGN'] = params["sign"]
        headers['OK-ACCESS-TIMESTAMP'] = params["timestamp"]
        headers['OK-ACCESS-PASSPHRASE'] = self._phrase
        #if "MONI" in self._phrase:
        #    headers['x-simulated-trading'] = '1' #模拟盘
        headers['x-simulated-trading'] = '1' #模拟盘
        return headers

    # 签名函数
    def signature(self, method="GET", path="", body=None):
        timestamp = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        params2 = {'timestamp': timestamp}
        message = params2["timestamp"] + method + path + ("" if (method == "GET") else json.dumps(body))
        mac = hmac.new(bytes(self._secret, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        params2["sign"] = base64.b64encode(mac.digest())
        return params2

    # http请求v2, headers单独传参
    def http_request_v2(self, url, method="GET", headers={}, params=None):
        headers['User-Agent'] = 'Mozilla/5.0 \(Windows NT 6.1; WOW64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/39.0.2171.71 Safari/537.36'
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                response = requests.post(url, data=params, headers=headers, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, data=params, headers=headers, timeout=5)
            result = response.json()
            # print(result)
            return result
        except Exception as e:
            print(repr(e))