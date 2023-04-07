from sdk import OKXV5

exchange = OKXV5(
    apikey="f07bd2f1-7876-4737-8434-f20fd2e3afe3", 
    secret="2B28083E8355FCA9359057166A5DB721", 
    phrase="QAczY8mYg9tSSg4%")
account_balance = exchange.account()
btc_balance=account_balance['BTC']['free']
usdt_balance=account_balance['USDT']['free']
symbol="BTC-USDT-SWAP"
info = exchange.order(symbol='BTC-USDT', 
                      side="SELL", 
                      type="LIMIT",
                      price='18991',
                      quantity=1, 
                      mode="CASH", 
                      )  #期货全仓买入做多
print(info)
