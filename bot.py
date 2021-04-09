import ccxt
import ta
import config
import pandas as pd

from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator, rsi

exchange = ccxt.binance(
    {"apiKey": config.BINANCE_API_KEY, "secret": config.BINANCE_SECRET_KEY}
)

markets = exchange.load_markets()

bars = exchange.fetch_ohlcv("BTC/EUR", limit=21, timeframe="1m")

df = pd.DataFrame(
    bars[:-1], columns=["timestamp", "open", "high", "low", "close", "volume"]
)

bb_indicator = BollingerBands(df["close"], window=1)

df["mavg"] = bb_indicator.bollinger_mavg()
df["upper_band"] = bb_indicator.bollinger_hband()
df["lower_band"] = bb_indicator.bollinger_lband()

atr_indicator = AverageTrueRange(df["high"], df["low"], df["close"])
df["atr"] = atr_indicator.average_true_range()

rsi_indicator = RSIIndicator(df["close"])
df["rsi"] = rsi_indicator.rsi()
print(df)