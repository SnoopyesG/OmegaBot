"""
Datei: breaker_blocks_func.py
Funktion: Findet Breaker Blocks (potenzielle Trendwendepunkte) in OHLCV-Daten.
Nutzung: breaker_blocks(df)
Beispiel siehe mini_skripte/trading_bot_demo.py
"""
def breaker_blocks(df):
    blocks = []
    for i in range(2, len(df)-2):
        if df['high'][i] > df['high'][i-2] and df['low'][i] < df['low'][i-2]:
            blocks.append({'index': i, 'high': df['high'][i], 'low': df['low'][i]})
    return blocks
