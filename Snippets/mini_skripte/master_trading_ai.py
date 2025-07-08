"""
master_trading_ai.py
Hauptskript: Steuert Datenimport, Analyse/ML, Backtest & (später) Bot.
"""

import pandas as pd
from machine_learning_export_framework import analyse_trades_ml  # Deine Hauptfunktion ins Framework verschieben!
# Beispiel: von trading_bot_demo import start_trading_bot

# === 1. Einstellungen ===
CSV_PATH = "trades.csv"

# === 2. Daten laden ===
def load_data(csv_path):
    print(f"Lade Daten aus {csv_path} ...")
    df = pd.read_csv(csv_path)
    print(df.head())
    return df

# === 3. ML-Analyse starten ===
def run_ml_analysis(df):
    # Die Funktion analyse_trades_ml musst du im Framework als eigene Funktion definieren!
    analyse_trades_ml(df)

# === 4. (Optional) Bot starten ===
def run_bot():
    # Hier würdest du z. B. deinen Trading-Bot starten.
    print("Trading-Bot starten... (TODO)")

# === 5. Hauptablauf ===
def main():
    df = load_data(CSV_PATH)
    run_ml_analysis(df)
    # run_bot()   # (später: auskommentieren oder per Option steuern)

if __name__ == "__main__":
    main()
