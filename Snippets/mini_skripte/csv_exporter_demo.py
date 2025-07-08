def main():
    import csv
    trades = [
        {'symbol': 'DOGE', 'side': 'BUY', 'price': 0.10, 'amount': 100, 'profit': 4},
        {'symbol': 'SHIB', 'side': 'SELL', 'price': 0.00002, 'amount': 100000, 'profit': 2},
    ]
    with open('trades.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=trades[0].keys())
        writer.writeheader()
        for t in trades:
            writer.writerow(t)
    print("Trades in trades.csv gespeichert!")

if __name__ == "__main__":
    main()
