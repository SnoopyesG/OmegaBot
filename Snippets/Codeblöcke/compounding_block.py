"""
Datei: compounding_block.py
Codeblock: Berechnet Compounding für Gewinne.
"""
def compound_balance(start_balance, trades, profit_per_trade):
    balance = start_balance
    for _ in range(trades):
        balance += balance * profit_per_trade
    return balance
