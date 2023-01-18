import base64
import hmac
import json
import time
import requests

from urllib.parse import urljoin


class OkexSpot:
   """OKEX Spot REST API client."""

   def __init__(self, symbol, access_key, secret_key, passphrase, host=None):
       self.symbol = symbol
       self._host = host or "https://aws.okx.com"
       self._access_key = access_key
       self._secret_key = secret_key
       self._passphrase = passphrase

   def request(self, method, uri, params=None, body=None, headers=None, auth=False):
       """Initiate network request
      @param method: request method, GET / POST / DELETE / PUT
      @param uri: request uri
      @param params: dict, request query params
      @param body: dict, request body
      @param headers: request http header
      @param auth: boolean, add permission verification or not
      """
       if params:
           query = "&".join(
              ["{}={}".format(k, params[k]) for k in sorted(params.keys())]
          )
           uri += "?" + query
       url = urljoin(self._host, uri)

       if auth:
           timestamp = (
                   str(time.time()).split(".")[0]
                   + "."
                   + str(time.time()).split(".")[1][:3]
          )
           if body:
               body = json.dumps(body)
           else:
               body = ""
           message = str(timestamp) + str.upper(method) + uri + str(body)
           mac = hmac.new(
               bytes(self._secret_key, encoding="utf8"),
               bytes(message, encoding="utf-8"),
               digestmod="sha256",
          )
           d = mac.digest()
           sign = base64.b64encode(d)

           if not headers:
               headers = {}
           headers["Content-Type"] = "application/json"
           headers["OK-ACCESS-KEY"] = self._access_key
           headers["OK-ACCESS-SIGN"] = sign
           headers["OK-ACCESS-TIMESTAMP"] = str(timestamp)
           headers["OK-ACCESS-PASSPHRASE"] = self._passphrase
       result = requests.request(
           method, url, data=body, headers=headers, timeout=10,verify=False
      ).json()
       if result.get("code") and result.get("code") != "0":
           return None, result
       return result, None

   def get_exchange_info(self):
       """Obtain trading rules and trading pair information."""
       uri = "/api/v5/public/instruments"
       params = {"instType": "SPOT", "instId": self.symbol}
       success, error = self.request(method="GET", uri=uri, params=params,verify=False)
       return success, error

   def get_orderbook(self):
       """
      Get orderbook data.
      """
       uri = "/api/v5/market/books"
       params = {"instId": self.symbol, "sz": 5}
       success, error = self.request(method="GET", uri=uri, params=params)
       return success, error

   def get_trade(self):
       """
      Get trade data.
      """
       uri = "/api/v5/market/trades"
       params = {"instId": self.symbol, "limit": 1}
       success, error = self.request(method="GET", uri=uri, params=params)
       return success, error

   def get_kline(self, interval):
       """
      Get kline data.
      :param interval: kline period.
      """
       if str(interval).endswith("h") or str(interval).endswith("d"):
           interval = str(interval).upper()
       uri = "/api/v5/market/candles"
       params = {"instId": self.symbol, "bar": interval, "limit": 200}
       success, error = self.request(method="GET", uri=uri, params=params)
       return success, error

   def get_asset(self, currency):
       """
      Get account asset data.
      :param currency: e.g. "USDT", "BTC"
      """
       params = {"ccy": currency}
       result = self.request(
           "GET", "/api/v5/account/balance", params=params, auth=True
      )
       return result

   def get_order_status(self, order_no):
       """Get order status.
      @param order_no: order id.
      """
       uri = "/api/v5/trade/order"
       params = {"instId": self.symbol, "ordId": order_no}
       success, error = self.request(method="GET", uri=uri, params=params, auth=True)
       return success, error

   def buy(self, price, quantity, order_type=None):
       """
      Open buy order.
      :param price:order price
      :param quantity:order quantity
      :param order_type:order type, "LIMIT" or "MARKET"
      :return:order id and None, otherwise None and error information
      """
       uri = "/api/v5/trade/order"
       data = {"instId": self.symbol, "tdMode": "cash", "side": "buy"}
       if order_type == "POST_ONLY":
           data["ordType"] = "post_only"
           data["px"] = price
           data["sz"] = quantity
       elif order_type == "MARKET":
           data["ordType"] = "market"
           data["sz"] = quantity  
       else:
           data["ordType"] = "limit"
           data["px"] = price
           data["sz"] = quantity
       success, error = self.request(method="POST", uri=uri, body=data, auth=True)
       if error:
           return None, error
       return success["data"][0]["ordId"], error

   def sell(self, price, quantity, order_type=None):
       """
      Close sell order.
      :param price:order price
      :param quantity:order quantity
      :param order_type:order type, "LIMIT" or "MARKET"
      :return:order id and None, otherwise None and error information
      """
       uri = "/api/v5/trade/order"
       data = {"instId": self.symbol, "tdMode": "cash", "side": "sell", "sz": quantity}
       if order_type == "POST_ONLY":
           data["ordType"] = "post_only"
           data["px"] = price
           data["sz"] = quantity
       elif order_type == "MARKET":
           data["ordType"] = "market"
           data["sz"] = quantity  
       else:
           data["ordType"] = "limit"
           data["px"] = price
           data["sz"] = quantity
       success, error = self.request(method="POST", uri=uri, body=data, auth=True)
       if error:
           return None, error
       return success["data"][0]["ordId"], error

   def revoke_order(self, order_no):
       """Cancel an order.
      @param order_no: order id
      """
       uri = "/api/v5/trade/cancel-order"
       data = {"instId": self.symbol, "ordId": order_no}
       _, error = self.request(method="POST", uri=uri, body=data, auth=True)
       if error:
           return order_no, error
       else:
           return order_no, None

   def revoke_orders(self, order_nos):
       """
      Cancel mutilple orders by order ids.
      @param order_nos :order list
      """
       success, error = [], []
       for order_id in order_nos:
           _, e = self.revoke_order(order_id)
           if e:
               error.append((order_id, e))
           else:
               success.append(order_id)
       return success, error

   def get_open_orders(self):
       """Get all unfilled orders.
      * NOTE: up to 100 orders
      """
       uri = "/api/v5/trade/orders-pending"
       params = {"instType": "SPOT", "instId": self.symbol}
       success, error = self.request(method="GET", uri=uri, params=params, auth=True)
       if error:
           return None, error
       else:
           order_ids = []
           if success.get("data"):
               for order_info in success["data"]:
                   order_ids.append(order_info["ordId"])
           return order_ids, None