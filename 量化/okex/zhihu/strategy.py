from lib2to3.pgen2.pgen import DFAState
from gary import OkexSpot

class Strategy:
    def __init__(self):
       self.exchange = OkexSpot(
           symbol="BTC-USDT",
            access_key="d8b0ca99-1037-4d70-988d-7521d7cd7449",
            secret_key="7A2D7339EFC6B18924FD7C911B414A4B",
            passphrase="QAczY8mYg9tSSg4%",
            host=None
        )
       print("Strategy start run...")
    def get_info(self):
        trade, error = self.exchange.get_trade()
        print("trade:", trade)
        print("error:", error)
if __name__ == '__main__':
    import time
    strategy = Strategy()
    strategy.get_info()