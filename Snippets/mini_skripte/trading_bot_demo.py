"""
Datei: trading_bot_demo.py
Mini-Skript: Zeigt Basisstruktur für Coin-Rotation mit Indikator-Check und Compounding.
"""
import pandas as pd
from ema_rsi_func import ema, rsi
from breaker_blocks_func import breaker_blocks
from compounding_block import compound_balance

# Beispiel-Daten
data = {
    'close': [10,11,12,13,12,11,13,14,12,10,11,13,15],
    'high':  [10,12,13,14,13,12,14,15,13,11,12,14,16],
    'low':   [9,10,11,12,11,10,12,13,11,9,10,12,14]
}
df = pd.DataFrame(data)

# Indikator-Checks
print("EMA:", ema(df['close'], 5).tolist())
print("RSI:", rsi(df['close'], 5).tolist())
print("Breaker Blocks:", breaker_blocks(df))

# Compounding
print("Balance nach 5 Trades mit 4% Gewinn:", compound_balance(100, 5, 0.04))
