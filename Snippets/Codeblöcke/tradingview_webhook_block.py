"""
Datei: tradingview_webhook_block.py
Codeblock: Webhook-Empfang für TradingView-Signale (Flask).
Zum Einbau in eigene Bots.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Empfangenes Signal:", data)
    # Hier: Signal verarbeiten
    return '', 200

if __name__ == '__main__':
    app.run(port=5000)
