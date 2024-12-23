# main.py (nur relevante Änderungen markiert)
import time
import threading
from logger import log_message
from performance_tracker import PerformanceTracker
from data_handler import fetch_market_data, analyze_market
from strategies import choose_strategy
from trade_executor import place_trade, get_open_trades
from bot_state import BotState
from trading_websocket import TradingWebSocket
from config import XTB_API_URL, TAKE_PROFIT_MULTIPLIER

tracker = PerformanceTracker()
ws_client = None
bot_thread = None
running = False

def log_signal(symbol, strategy, price):
    signals = BotState.get_state().get("signals", [])
    signal_entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "symbol": symbol,
        "action": strategy,
        "price": price
    }
    signals.append(signal_entry)
    BotState.get_state()["signals"] = signals
    log_message("info", f"Signal erkannt: {strategy} {symbol} bei {price}")

def main_loop():
    global ws_client, tracker, running
    ping_thread = threading.Thread(target=ws_client.keep_alive, daemon=True)
    ping_thread.start()

    while running:
        if not BotState.get_state()["connected"]:
            time.sleep(1)
            continue

        if not BotState.get_state()["trading_active"]:
            time.sleep(5)
            continue

        market_status = {}
        markets = BotState.get_state()["markets_to_watch"]
        log_message("info", f"Starte neuen Analysezyklus. Märkte: {markets}")

        for symbol in markets:
            log_message("info", f"Beginne Marktdatenabruf für {symbol}.")
            data = fetch_market_data(ws_client, symbol, "H1", ws_client.session_id)
            if data is None or len(data) < 20:
                log_message("warning", f"Keine ausreichenden Daten für {symbol}.")
                continue

            tendency, direction = analyze_market(data)
            log_message("info", f"{symbol} - Tendenz: {tendency}, Richtung: {direction}")
            market_status[symbol] = {"tendency": tendency, "direction": direction}

            strategy = choose_strategy(tendency, direction, data)
            log_message("info", f"{symbol} - Strategieentscheidung: {strategy}")

            # Vor dem Trade prüfen, ob bereits Position in gleicher Richtung offen ist
            positions = BotState.get_state().get("positions", {})
            # If direction == "up" und strategy == "buy" => wir wollen long
            # If direction == "down" und strategy == "sell" => wir wollen short
            # Bei buy: long, bei sell: short
            desired_pos = "long" if strategy == "buy" else ("short" if strategy == "sell" else None)

            if strategy in ("buy", "sell"):
                # Prüfen, ob bereits position vorhanden
                current_pos = positions.get(symbol)
                if current_pos == desired_pos:
                    log_message("info", f"Bereits eine {desired_pos}-Position für {symbol} offen. Kein neuer Trade.")
                    continue

                volume = 0.1
                risk = 0.005
                sl = risk
                tp = risk * TAKE_PROFIT_MULTIPLIER
                place_trade(ws_client, symbol, volume, strategy, sl, tp)
                simulated_pnl = (tp - sl) if strategy == "buy" else (sl - tp)
                tracker.log_trade(simulated_pnl)

                current_price = data[-1]["close"]
                log_signal(symbol, strategy, current_price)

        BotState.update_markets(market_status)
        open_trades = get_open_trades(ws_client)
        BotState.update_open_trades(open_trades)

        perf = tracker.summary()
        BotState.update_performance(perf)

        log_message("info", f"Performance: {perf}")
        time.sleep(30)

def start_bot():
    global ws_client, bot_thread, running
    if running:
        log_message("warning", "Bot läuft bereits")
        return
    running = True
    ws_client = TradingWebSocket(XTB_API_URL)
    connected = ws_client.connect()
    if not connected:
        running = False
        return
    bot_thread = threading.Thread(target=main_loop, daemon=True)
    bot_thread.start()
    log_message("info", "Bot gestartet")

def stop_bot():
    global running, ws_client
    running = False
    if ws_client and ws_client.ws:
        ws_client.ws.close()
    BotState.disconnect()
    if bot_thread:
        bot_thread.join()
    log_message("info", "Bot gestoppt")

if __name__ == "__main__":
    start_bot()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_bot()
