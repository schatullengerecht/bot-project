# data_handler.py
import time
import numpy as np
from logger import log_message

def fetch_market_data(ws, symbol: str, period: str, session_id: str, timeout: int = 15):
    end_time = int(time.time() * 1000)
    start_time = end_time - (24 * 60 * 60 * 1000)

    period_map = {
        "M1": 1, "M5": 5, "M15": 15, "M30": 30,
        "H1": 60, "H4": 240, "D1": 1440
    }
    if period not in period_map:
        period = "H1"
    p = period_map[period]

    request = {
        "command": "getChartRangeRequest",
        "arguments": {
            "info": {
                "symbol": symbol,
                "period": p,
                "start": start_time,
                "end": end_time
            },
            "streamSessionId": session_id
        }
    }

    ws.send_json(request)
    log_message("info", f"Marktdaten für {symbol} angefragt.")

    data = ws.wait_for_data("chart_data", timeout=timeout)
    if data is None:
        log_message("error", f"Keine Marktdaten für {symbol} erhalten.")
        return None

    if isinstance(data, dict) and data.get("status") == False:
        log_message("error", f"Fehler bei der Marktdatenanfrage für {symbol}: {data.get('errorDescr')}")
        return None

    digits = data["digits"]
    rateInfos = data.get("rateInfos", [])

    if len(rateInfos) < 20:
        log_message("warning", f"Zu wenige Marktdaten für {symbol} erhalten ({len(rateInfos)} Kerzen).")
        return None

    candles = []
    for r in rateInfos:
        base = r["open"] / (10**digits)
        c = (r["open"] + r["close"]) / (10**digits)
        h = (r["open"] + r["high"]) / (10**digits)
        l = (r["open"] + r["low"]) / (10**digits)
        o = base
        candles.append({
            "time": r["ctm"] / 1000,
            "open": o,
            "close": c,
            "high": h,
            "low": l,
            "volume": r["vol"]
        })

    return candles

def calculate_atr(data):
    highs = [c["high"] for c in data]
    lows = [c["low"] for c in data]
    closes = [c["close"] for c in data[:-1]]

    tr = [max(h - l, abs(h - c), abs(l - c))
          for h, l, c in zip(highs[1:], lows[1:], closes)]
    if len(tr) < 14:
        return None
    return np.mean(tr[-14:])

def calculate_adx(data):
    if len(data) < 15:
        return None
    closes = [c["close"] for c in data]
    highs = [c["high"] for c in data]
    lows = [c["low"] for c in data]

    tr = [max(h - l, abs(h - pc), abs(l - pc))
          for h, l, pc in zip(highs[1:], lows[1:], closes[:-1])]
    if len(tr) < 14:
        return None
    atr = np.mean(tr[-14:])

    plus_dm = [highs[i] - highs[i - 1] if highs[i] > highs[i - 1] else 0 for i in range(1, len(highs))]
    minus_dm = [lows[i - 1] - lows[i] if lows[i - 1] > lows[i] else 0 for i in range(1, len(lows))]

    if len(plus_dm) < 14 or len(minus_dm) < 14:
        return None

    smoothed_plus_dm = np.mean(plus_dm[-14:])
    smoothed_minus_dm = np.mean(minus_dm[-14:])
    plus_di = 100 * (smoothed_plus_dm / atr)
    minus_di = 100 * (smoothed_minus_dm / atr)
    dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
    return dx

def calculate_bollinger(data):
    if len(data) < 20:
        return None, None
    closes = [c["close"] for c in data]
    recent = closes[-20:]
    mean = np.mean(recent)
    std_dev = np.std(recent)
    upper = mean + (2 * std_dev)
    lower = mean - (2 * std_dev)
    return upper, lower

def analyze_market(data):
    if data is None or len(data) < 20:
        return ("unknown", "flat")

    atr = calculate_atr(data)
    adx = calculate_adx(data)
    upper, lower = calculate_bollinger(data)

    # Richtung bestimmen (up/down/flat):
    direction = "flat"
    if data[-1]["close"] > data[-2]["close"]:
        direction = "up"
    elif data[-1]["close"] < data[-2]["close"]:
        direction = "down"

    if atr is None or adx is None or upper is None or lower is None:
        return ("unknown", direction)

    # Bisherige Logik für Tendenz:
    tendency = "unknown"
    if np.mean(adx) > 25:
        tendency = "trend"
    elif lower < atr < upper:
        tendency = "sideways"

    return (tendency, direction)
