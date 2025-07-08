import os
import csv
import pandas as pd
import numpy as np
import yfinance as yf
import talib
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import mean_squared_error
import joblib  # Zum Speichern und Laden des Modells
from binance.client import Client
import tkinter as tk

# Funktion zum Erstellen von EMA
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

# Funktion zum Erstellen von RSI
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Funktion zum Erstellen von MACD
def macd(series, fast=12, slow=26, signal=9):
    macd_line, signal_line, _ = talib.MACD(series, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return macd_line, signal_line

# Funktion zum Erstellen von Bollinger Bands
def bollinger_bands(series, timeperiod=20, nbdevup=2, nbdevdn=2):
    upperband, middleband, lowerband = talib.BBANDS(series, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
    return upperband, middleband, lowerband

# Funktion zum Speichern von Trades in CSV
def log_trade(trade, filename="trades.csv"):
    write_header = not os.path.isfile(filename)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["coin", "action", "price", "balance", "profit", "rsi", "ema_fast", "ema_slow", "status"])
        writer.writerow(trade)

# Funktion zum Berechnen des Profits
def microcompound(balance, profit):
    return balance + profit

# Funktion zum Laden von historischen Preisen
def load_historical_prices(symbol):
    yf_symbols = {
        "bitcoin": "BTC-USD",
        "dogecoin": "DOGE-USD",
        "shiba-inu": "SHIB-USD"
    }
    yf_symbol = yf_symbols.get(symbol)
    if not yf_symbol:
        print(f"Kein YFinance-Symbol für {symbol}")
        return None, None, None

    data = yf.download(yf_symbol, period="3mo", interval="1h", auto_adjust=True)
    if data.empty:
        print(f"Keine historischen Daten geladen für {symbol}")
        return None, None, None

    def ensure_1d(series_or_df):
        if isinstance(series_or_df, pd.DataFrame):
            return series_or_df.iloc[:, 0]
        return series_or_df

    close = ensure_1d(data['Close']).reset_index(drop=True)
    high = ensure_1d(data['High']).reset_index(drop=True)
    low = ensure_1d(data['Low']).reset_index(drop=True)

    return close, high, low

# Funktion zur Berechnung der Positionsgröße mit Risikomanagement
def position_size(capital, entry_price, stop_loss_price, risk_per_trade=0.02):
    max_loss = capital * risk_per_trade  # Maximaler Verlust basierend auf dem Risiko
    risk_per_unit = abs(entry_price - stop_loss_price)  # Berechnung des Risikos je Einheit
    if risk_per_unit == 0:
        return 0
    size = max_loss / risk_per_unit  # Berechnung der maximalen Positionsgröße
    max_affordable_size = capital / entry_price  # Maximal erschwingliche Menge basierend auf dem Kapital
    return min(size, max_affordable_size)  # Rückgabe der kleineren der beiden Werte

# Fehlererkennungsfunktion, um ungünstige Trades zu identifizieren
def error_analysis(prev_balance, current_balance):
    if current_balance < prev_balance:
        return True
    return False

# Funktion für das Lernen aus vergangenen Trades (SGD-Classifier)
def learn_from_past_trades(model, data, target):
    if len(data) > 0:
        model.fit(data, target)
        return model
    return model

# Funktion zum Abrufen der Echtzeitpreise von Binance
def get_real_time_price(symbol="BTCUSDT"):
    client = Client(api_key='your_api_key', api_secret='your_api_secret')
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

# Funktion zur Durchführung des Backtests mit Lernkomponente und Fehlererkennung
def run_backtest(coins, mode="long", start_balance=1000.0, risk_per_trade=0.02, min_investment=10):
    balance = start_balance
    max_positions = 5
    positions = []
    model = SGDClassifier(loss="log", max_iter=1000, tol=1e-3)  # Online Learning mit SGD

    # Lern-Daten für das Modell (RSI, EMA, Preis)
    X_data = []
    y_data = []

    prev_balance = balance  # Speicherung des vorherigen Kontostands

    for coin in coins:
        print(f"\nStarte Backtest für {coin} mit Startkapital {balance:.2f}€ ({mode})")
        prices, high, low = load_historical_prices(coin)
        if prices is None or prices.empty:
            print(f"Keine historischen Daten für {coin}, überspringe Coin.")
            continue

        prices = prices.head(100)
        high = high.head(100)
        low = low.head(100)

        ema_fast = ema(prices, 15)
        ema_slow = ema(prices, 45)
        rsi_vals = rsi(prices)
        sma50 = talib.SMA(prices.values, timeperiod=50)
        atr = talib.ATR(high.values, low.values, prices.values, timeperiod=14)
        macd_line, signal_line = macd(prices)
        upperband, middleband, lowerband = bollinger_bands(prices)

        for i in range(50, len(prices)):  # Ab SMA50
            price = prices.iat[i]
            rsi_value = rsi_vals.iat[i]
            atr_value = atr[i]
            sma_value = sma50[i]

            if np.isnan(atr_value) or np.isnan(sma_value):
                continue

            if mode == "long":
                bullish = (ema_fast.iat[i] > ema_slow.iat[i]) and (rsi_value > 50) and (price > sma_value)
                bearish = (ema_fast.iat[i] < ema_slow.iat[i]) and (rsi_value < 50) and (price < sma_value)
            elif mode == "short":
                bullish = (ema_fast.iat[i] < ema_slow.iat[i]) and (rsi_value < 50) and (price < sma_value)
                bearish = (ema_fast.iat[i] > ema_slow.iat[i]) and (rsi_value > 50) and (price > sma_value)

            to_close = []
            for idx, pos in enumerate(positions):
                current_profit_pct = (price - pos['entry_price']) / pos['entry_price']
                if current_profit_pct >= pos['take_profit'] or current_profit_pct <= -pos['stop_loss']:
                    profit = (price - pos['entry_price']) * pos['amount']
                    balance = microcompound(balance, profit)
                    log_trade([pos['coin'], "sell", price, round(balance, 2), round(profit, 2), rsi_value, ema_fast.iat[i], ema_slow.iat[i], 'Take-Profit' if current_profit_pct >= pos['take_profit'] else 'Stop-Loss'])
                    status = "Take-Profit" if current_profit_pct >= pos['take_profit'] else "Stop-Loss"
                    print(f"{pos['coin']}: {status} bei {price:.2f}€, Gewinn/Verlust: {profit:.2f}€, Kapital: {balance:.2f}€")
                    to_close.append(idx)

            for idx in reversed(to_close):
                positions.pop(idx)

            if bullish and len(positions) < max_positions:
                stop_loss_price = price - 1.5 * atr_value
                take_profit_price = price + 3 * atr_value
                stop_loss_pct = abs(stop_loss_price - price) / price
                take_profit_pct = abs(take_profit_price - price) / price
                size = position_size(balance, price, stop_loss_price, risk_per_trade)

                if size * price >= min_investment and size > 0:
                    positions.append({
                        'coin': coin,
                        'entry_price': price,
                        'amount': size,
                        'stop_loss': stop_loss_pct,
                        'take_profit': take_profit_pct
                    })
                    invest = size * price
                    balance -= invest
                    log_trade([coin, "buy", price, round(balance, 2), 0, rsi_value, ema_fast.iat[i], ema_slow.iat[i], 'Buy'])
                    print(f"{coin}: Kaufe {size:.4f} Einheiten bei {price:.2f}€, investiere {invest:.2f}€, Kapital: {balance:.2f}€")

            if bearish:
                to_close_bear = [idx for idx, pos in enumerate(positions) if pos['coin'] == coin]
                for idx in reversed(to_close_bear):
                    pos = positions[idx]
                    profit = (price - pos['entry_price']) * pos['amount']
                    balance = microcompound(balance, profit)
                    log_trade([pos['coin'], "sell", price, round(balance, 2), round(profit, 2), rsi_value, ema_fast.iat[i], ema_slow.iat[i], 'Bearish'])
                    print(f"{pos['coin']}: Bärischer Markt - Verkauf bei {price:.2f}€, Gewinn/Verlust: {profit:.2f}€, Kapital: {balance:.2f}€")
                    positions.pop(idx)

        # Fehleranalyse durchführen
        if error_analysis(prev_balance, balance):
            print(f"Fehler erkannt: Verlusttrade! Versuche, die Strategie anzupassen und andere Ressourcen zu verwenden.")
            X_data.append([rsi_value, ema_fast.iat[i], ema_slow.iat[i]])  # Merkmale für das Modell
            y_data.append(-1)  # Negatives Ergebnis bedeutet Verlust
            model = learn_from_past_trades(model, np.array(X_data), np.array(y_data))
            joblib.dump(model, 'trade_model.pkl')  # Speichern des verbesserten Modells

    print(f"\nBacktest beendet, Endkapital: {balance:.2f}€")
    return balance

# GUI zur Anzeige von Trading-Statistiken
def create_gui():
    root = tk.Tk()
    root.title("Trading Bot")

    label = tk.Label(root, text="Trading Status")
    label.pack()

    root.mainloop()

def main():
    mode = input("Willst du long, short oder auto testen? (long/short/auto): ").strip().lower()
    coins = ["bitcoin", "dogecoin", "shiba-inu"]

    if mode == "auto":
        long_profits = []
        short_profits = []
        for _ in range(5):
            long_profits.append(run_backtest(coins, "long"))
            short_profits.append(run_backtest(coins, "short"))
        avg_long = sum(long_profits) / len(long_profits)
        avg_short = sum(short_profits) / len(short_profits)
        print(f"\nDurchschnittlicher Long Gewinn: {avg_long:.2f}€")
        print(f"Durchschnittlicher Short Gewinn: {avg_short:.2f}€")
        if avg_long > avg_short:
            print("Long ist profitabler. Starte finalen Long-Backtest.")
            run_backtest(coins, "long")
        else:
            print("Short ist profitabler. Starte finalen Short-Backtest.")
            run_backtest(coins, "short")
    else:
        run_backtest(coins, mode)

if __name__ == "__main__":
    main()
