import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

symbol = 'BTC-USD'
df = yf.download(symbol, period='6mo', interval='4h')

# Indikatoren berechnen
df['EMA15'] = df['Close'].ewm(span=15).mean()
df['EMA45'] = df['Close'].ewm(span=45).mean()
delta = df['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# Buy/Sell-Strategie (optimiert auf Buchlogik)
df['Buy'] = (df['EMA15'] > df['EMA45']) & (df['EMA15'].shift(1) <= df['EMA45'].shift(1)) & (df['RSI'] < 40)
df['Sell'] = ((df['EMA15'] < df['EMA45']) & (df['EMA15'].shift(1) >= df['EMA45'].shift(1))) | (df['RSI'] > 65)

trades = []
position = None
for i, row in df.iterrows():
    buy_signal = bool(row['Buy'])
    sell_signal = bool(row['Sell'])
    if position is None and buy_signal:
        entry = row['Close']
        entry_time = i
        position = {'entry': entry, 'time': entry_time}
    elif position is not None and sell_signal:
        exit = row['Close']
        profit = exit - position['entry']
        trades.append({'entry_time': position['time'], 'entry': position['entry'],
                       'exit_time': i, 'exit': exit, 'profit': profit})
        position = None

profits = [t['profit'] for t in trades]
print(f"Anzahl Trades: {len(trades)}, Gewinnrate: {np.mean([p>0 for p in profits])*100:.1f}%, Ø Gewinn/Trade: {np.mean(profits):.2f} USD")

plt.figure(figsize=(15,7))
plt.plot(df['Close'], label='BTCUSDT')
plt.plot(df['EMA15'], '--', label='EMA15')
plt.plot(df['EMA45'], '--', label='EMA45')
buys = df[df['Buy']]
sells = df[df['Sell']]
plt.scatter(buys.index, buys['Close'], marker='^', color='g', label='Buy', s=80)
plt.scatter(sells.index, sells['Close'], marker='v', color='r', label='Sell', s=80)
plt.title('BTCUSDT Backtest (EMA Crossover + RSI) – 4h Chart')
plt.legend()
plt.show()
