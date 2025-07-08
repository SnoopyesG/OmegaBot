import csv

def log_trade(trade):
    with open("trades.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(trade)
