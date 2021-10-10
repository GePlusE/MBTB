import os
import config
import pandas as pd
import ta
from time import sleep
from binance.client import Client
from binance.exceptions import BinanceAPIException

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)


def get_data(symbol, interval="1m", offset="30"):
    try:
        df = pd.DataFrame(
            client.get_historical_klines(symbol, interval, offset + " m ago UTC")
        )
        sleep(0.5)
    except BinanceAPIException as e:
        print(e)
        sleep(20)
        df = pd.DataFrame(
            client.get_historical_klines(symbol, interval, offset + " m ago UTC")
        )
    df = df.iloc[:, :6]
    df.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    df = df.set_index("Time")
    df.index = pd.to_datetime(df.index, unit="ms")
    df = df.astype(float)
    return df


def trading_MACD(symbol, qty, open_position=False):
    while True:
        df = get_data(symbol, offset="100")
        if not open_position:
            if (
                ta.trend.macd_diff(df.Close).iloc[-1] > 0
                and ta.trend.macd_diff(df.Close).iloc[-2] < 0
            ):
                order = client.create_order(
                    symbol=symbol, side="BUY", type="MARKET", quantity=qty
                )
                open_position = True
                buyprice = float(order["fills"][0]["price"])
                print(order)
                print(f"Bought at {buyprice}")
                os.system('say "Successfully ordered."')
                break

    if open_position:
        while True:
            df = get_data(symbol, offset="100")
            if ta.trend.macd_diff(df.Close).iloc[-1] < 0:
                order = client.create_order(
                    symbol=symbol, side="SELL", type="MARKET", quantity=qty
                )
                open_position = True
                sellprice = float(order["fills"][0]["price"])
                print(order)
                print(f"Sold at {sellprice}")
                print(f"profit = {(sellprice - buyprice)/buyprice:.2%}")
                os.system('say "Successfully sold."')
                open_position = False
                break


print("running...")
os.system('say "Running... Started script."')
while True:
    trading_MACD("BTCUSDT", qty=0.0005)  # 43.96813704 USDT / 0.01955815BNB (6,81€)

print(client.get_account())