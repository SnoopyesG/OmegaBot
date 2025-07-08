#grundstein für Bot/Rotator die Daten überhaupt zu empfangen..
import yfinance as yf

symbol = "DOGE-USD"
data = yf.download(symbol, period="7d", interval="1h")

data.to_csv("doge_data.csv")
print("Daten gespeichert in doge_data.csv")
