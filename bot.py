import ccxt
import ta
import config
import pandas as pd

from ta.volatility import BollingerBands, AverageTrueRange

exchange = ccxt.binance(
    {"apiKey": config.BINANCE_API_KEY, "secret": config.BINANCE_SECRET_KEY}
)

markets = exchange.load_markets()

bars = exchange.fetch_ohlcv("BTC/EUR", limit=21, timeframe="1m")

df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

bb_indicator = BollingerBands(df["close"], window=2)

df["mavg"] = bb_indicator.bollinger_mavg()
df["upper_band"] = bb_indicator.bollinger_hband()
df["lower_band"] = bb_indicator.bollinger_lband()
print(df)