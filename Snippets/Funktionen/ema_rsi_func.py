"""
Datei: ema_rsi_func.py
Funktionen:
- EMA-Berechnung
- RSI-Berechnung
Nutzung: ema(series, period), rsi(series, period)
"""
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
