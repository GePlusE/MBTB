import ccxt
import ta
import config
import pandas as pd

from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator, rsi


def load_data():
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    exchange = ccxt.binance(
        {"apiKey": config.BINANCE_API_KEY, "secret": config.BINANCE_SECRET_KEY}
    )

    markets = exchange.load_markets()

    bars = exchange.fetch_ohlcv("BTC/EUR", timeframe="1m", limit=9999)

    df = pd.DataFrame(
        bars[:-1], columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    bb_indicator = BollingerBands(df["close"], window=1)

    df["ma_50"] = df.iloc[:, 1].rolling(window=50).mean()
    df["mavg"] = bb_indicator.bollinger_mavg()
    df["upper_band"] = bb_indicator.bollinger_hband()
    df["lower_band"] = bb_indicator.bollinger_lband()

    atr_indicator = AverageTrueRange(df["high"], df["low"], df["close"])
    df["atr"] = atr_indicator.average_true_range()

    rsi_indicator = RSIIndicator(df["close"])
    df["rsi"] = rsi_indicator.rsi()

    return df


def script(dataframe, balance, qty):
    df = dataframe
    p_close = df["close"].values[-3]
    c_close = df["close"].values[-2]
    l_close = df["close"].values[-1]
    p_ma_50 = df["ma_50"].values[-3]
    c_ma_50 = df["ma_50"].values[-2]

    if p_close > p_ma_50 and c_close < c_ma_50 and balance > 0:
        qty += (balance * 0.999) / l_close
        balance = 0
        print(
            f"Bought for {c_close:.2f}. Total QTY now: {qty:.5f} / Balance at {balance:.2f}."
        )
    elif p_close < p_ma_50 and c_close > c_ma_50 and qty > 0:
        balance += (qty * l_close) * 0.999
        qty = 0
        print(
            f"Sold for {c_close:.2f}. Total QTY now: {qty:.5f} / Balance at {balance:.2f}."
        )
    else:
        pass
    return balance, qty


df = load_data()
len = len(df)
Balance = 1000
qty = 0
counter = 5
l_close = df["close"].values[-1]


for i in range(len):
    sub_df = df.head(counter)
    counter += 1

    Balance, qty = script(sub_df, Balance, qty)
if qty == 0:
    print(f"Balance at {Balance:.2f} and QTY at {qty:.5f}.")
else:
    Balance += (qty * l_close) * 0.999
    qty = 0
    print(f"Balance at {Balance:.2f} and QTY at {qty:.5f}.")
