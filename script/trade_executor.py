# trade_executor.py
import time
import json
from logger import log_message

def place_trade(ws, symbol, volume, order_type, sl, tp):
    trade_request = {
        "command": "tradeTransaction",
        "arguments": {
            "tradeTransInfo": {
                "cmd": order_type,  # 0=buy, 1=sell laut XTB-Doku
                "symbol": symbol,
                "volume": volume,
                "type": 0,  # Marktorder
                "sl": sl,
                "tp": tp
            }
        }
    }
    ws.send_json(trade_request)
    log_message("info", f"Trade ausgeführt: {order_type} {volume} {symbol} SL:{sl} TP:{tp}")

    # Auf Bestätigung warten
    response = ws.wait_for_data("tradeTransaction", timeout=10)
    if response is None:
        log_message("warning", f"Keine Antwort auf tradeTransaction für {symbol}.")
    else:
        if response.get("status") == False:
            log_message("error", f"Fehler bei tradeTransaction für {symbol}: {response.get('errorDescr')}")
        else:
            log_message("info", f"TradeTransaction erfolgreich bestätigt für {symbol}.")


def get_open_trades(ws):
    open_trades_request = {"command": "getTrades", "arguments": {"openedOnly": True}}
    ws.send_json(open_trades_request)
    log_message("info", "Frage offene Trades von der API ab...")

    response = ws.wait_for_data("trades", timeout=10)
    if response is None:
        log_message("warning", "Keine Antwort auf getTrades erhalten.")
        return []

    if isinstance(response, dict) and response.get("status") == False:
        log_message("error", f"Fehler beim Abrufen der offenen Trades: {response.get('errorDescr','Unbekannt')}")
        return []

    raw_trades = response.get("returnData", [])
    trades = []
    for t in raw_trades:
        # Annahme: laut XTB-API gibt es ein cmd Feld: 0=buy(long), 1=sell(short)
        # Prüfe in der Doku für getTrades, welche Felder genau zurückgegeben werden.
        # Falls die API andere Felder für cmd nutzt oder dieses Feld nicht verfügbar ist,
        # passe dies entsprechend an.
        trades.append({
            "trade_id": t.get("position"),
            "symbol": t.get("symbol"),
            "open_price": t.get("open_price"),
            "current_price": t.get("close_price", t.get("open_price")),
            "volume": t.get("volume", 0.1),
            "cmd": t.get("cmd")  # 0=long, 1=short
        })

    return trades
