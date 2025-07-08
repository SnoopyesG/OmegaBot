"""
Datei: csv_logging_block.py
Codeblock: Loggt Trades in eine CSV-Datei.
"""
import csv

def log_trade_to_csv(filename, trade_dict):
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=trade_dict.keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(trade_dict)
