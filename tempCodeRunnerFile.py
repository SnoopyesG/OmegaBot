import os
import csv
import pandas as pd
import numpy as np
import yfinance as yf
import talib


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def log_trade(trade, filename="trades.csv"):
    write_header = not os.path.isfile(filename)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["coin", "action", "price", "balance", "profit"])
        writer.writerow(trade)


def microcompound(balance, profit):
    return balance + profit


def load_historical_prices(symbol):
    yf_symbols = {
        "bitcoin": "BTC-USD",
        "dogecoin": "DOGE-USD",
        "shiba-inu": "SHIB-USD"
    }
    yf_symbol = yf_symbols.get(symbol)
    if not yf_symbol:
        print(f"Kein YFinance-Symbol für {symbol}")
        return None

    data = yf.download(yf_symbol, period="1mo", interval="1h", auto_adjust=True)
    if data.empty:
        print(f"Keine historischen Daten geladen für {symbol}")
        return None

    close_prices = data['Close']
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]
    return close_prices.reset_index(drop=True), data['High'].reset_index(drop=True), data['Low'].reset_index(drop=True)


def position_size(capital, entry_price, stop_loss_price, risk_per_trade=0.02):
    max_loss = capital * risk_per_trade
    risk_per_unit = abs(entry_price - stop_loss_price)
    if risk_per_unit == 0:
        return 0
    size = max_loss / risk_per_unit
    return size


def run_backtest(coins, mode="long", start_balance=1000.0, risk_per_trade=0.02, min_investment=10):
    balance = start_balance
    max_positions = 5
    positions = []

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

        for i in range(50, len(prices)):  # ab 50 wegen SMA50
            price = prices.iat[i]
            rsi_value = rsi_vals.iat[i]
            atr_value = atr[i]
            sma_value = sma50[i]
            if np.isnan(atr_value) or np.isnan(sma_value):
                continue

            # Trendfilter (SMA50) + EMA + RSI für Bull/Bear
            if mode == "long":
                bullish = (ema_fast.iat[i] > ema_slow.iat[i]) and (rsi_value > 50) and (price > sma_value)
                bearish = (ema_fast.iat[i] < ema_slow.iat[i]) and (rsi_value < 50) and (price < sma_value)
            elif mode == "short":
                bullish = (ema_fast.iat[i] < ema_slow.iat[i]) and (rsi_value < 50) and (price < sma_value)
                bearish = (ema_fast.iat[i] > ema_slow.iat[i]) and (rsi_value > 50) and (price > sma_value)
            else:
                bullish = (ema_fast.iat[i] > ema_slow.iat[i]) and (rsi_value > 50) and (price > sma_value)
                bearish = (ema_fast.iat[i] < ema_slow.iat[i]) and (rsi_value < 50) and (price < sma_value)

            # Positionen schließen bei Take-Profit / Stop-Loss (dynamisch über ATR)
            to_close = []
            for idx, pos in enumerate(positions):
                current_profit_pct = (price - pos['entry_price']) / pos['entry_price']
                if current_profit_pct >= pos['take_profit'] or current_profit_pct <= -pos['stop_loss']:
                    profit = (price - pos['entry_price']) * pos['amount']
                    balance = microcompound(balance, profit)
                    log_trade([pos['coin'], "sell", price, round(balance, 2), round(profit, 2)])
                    status = "Take-Profit" if current_profit_pct >= pos['take_profit'] else "Stop-Loss"
                    print(f"{pos['coin']}: {status} bei {price:.2f}€, Gewinn/Verlust: {profit:.2f}€, Kapital: {balance:.2f}€")
                    to_close.append(idx)

            for idx in reversed(to_close):
                positions.pop(idx)

            # Neue Position eröffnen, wenn bullish & Platz frei
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
                    log_trade([coin, "buy", price, round(balance, 2), 0])
                    print(f"{coin}: Kaufe {size:.4f} Einheiten bei {price:.2f}€, investiere {invest:.2f}€, Kapital: {balance:.2f}€")
                else:
                    print(f"{coin}: Position zu klein (Investition < {min_investment}€), kaufe nicht.")

            # Bei bärischem Markt alle Positionen des Coins schließen
            if bearish:
                to_close_bear = [idx for idx, pos in enumerate(positions) if pos['coin'] == coin]
                for idx in reversed(to_close_bear):
                    pos = positions[idx]
                    profit = (price - pos['entry_price']) * pos['amount']
                    balance = microcompound(balance, profit)
                    log_trade([pos['coin'], "sell", price, round(balance, 2), round(profit, 2)])
                    print(f"{pos['coin']}: Bärischer Markt - verkaufe bei {price:.2f}€, Gewinn/Verlust: {profit:.2f}€, Kapital: {balance:.2f}€")
                    positions.pop(idx)

    # Offene Positionen am Ende schließen
    for pos in positions:
        price = prices.iat[-1]
        profit = (price - pos['entry_price']) * pos['amount']
        balance = microcompound(balance, profit)
        log_trade([pos['coin'], "sell", price, round(balance, 2), round(profit, 2)])
        print(f"{pos['coin']}: Backtest Ende - verkaufe offene Position bei {price:.2f}€, Gewinn/Verlust: {profit:.2f}€, Kapital: {balance:.2f}€")

    print(f"\nBacktest beendet, Endkapital: {balance:.2f}€")
    return balance


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
