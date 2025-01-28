# This algotrading bot uses two technical indicators: SMA and RSI. I am using SMA instead of simple price levels
# given in the example of the task because it is much more realistic.


import pandas as pd
import yfinance as yf
import ta
from backtesting import Strategy
from backtesting import Backtest

# Downloading financial data from Yahoo Finance as a pandas dataframe using the yfinance library
data = yf.download("AAPL", start="2000-12-30", end="2024-12-30")
data.index = pd.to_datetime(data.index)

# Calculating SMA for 50 days and 200 days
data["SMA50"] = data["Close"].rolling(window=50).mean()
data["SMA200"] = data["Close"].rolling(window=200).mean()

# Calculate RSI for 14 days using built in functions in the ta library
data["RSI"] = ta.momentum.RSIIndicator(data["Close"], window=14).rsi()

# Function to generate buying and selling signals. 1 means buy and -1 means sell.
# Buy signal is generated when the 50-day-SMA is greater than the 200-day-SMA and the RSI is below 30.
# Sell signal is generated when the 50-day-SMA is lower than the 200-day-SMA and the RSI is above 80.
def GenSignal(row):
    if row["SMA50"] > row["SMA200"] and row["RSI"] < 30:
        return 1
    elif row["SMA50"] < row["SMA200"] and row["RSI"] > 80:
        return -1
    else:
        return 0

# Adding Signal column to pandas dataframe
data["Signal"] = data.apply(GenSignal, axis=1)


def SIGNAL():
    return data.Signal

# Checking whether strategy works properly or not by counting the number of buying and selling signals.
print(data.head())
print(data.tail())
print("Number of buy signals: ", data.Signal.value_counts()[1])
print("Number of sell signals: ", data.Signal.value_counts()[-1])

# Cleaning data by dropping all null values
ohlc_data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Signal']].dropna()
ohlc_data.reset_index(inplace=True)

# Class which defines the strategy
class CustStrat(Strategy):

    # Initializing the variable signal1 and defining the indicator as the SIGNAL() fucntion
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        if self.signal1 == 1 and not self.position:
            # Buy with a stop-loss at 10% below the entry price
            self.buy(sl=self.data.Close[-1] * 0.90)
        elif self.signal1 == -1 and self.position:
            # Close the position when a sell signal occurs
            self.position.close()


bt = Backtest(ohlc_data, CustStrat, cash=10_000)
output = bt.run()
print(output)
bt.plot()
