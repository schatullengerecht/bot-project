# strategies.py
import numpy as np

def rsi(data):
    if len(data) < 15:
        return 50
    closes = [c["close"] for c in data]
    deltas = np.diff(closes)
    seed = deltas[:14]
    up = seed[seed > 0].sum() / 14 if len(seed[seed > 0]) > 0 else 0
    down = -seed[seed < 0].sum() / 14 if len(seed[seed < 0]) > 0 else 0
    if down == 0:
        return 100
    rs = up/down
    return 100 - (100/(1+rs))

def moving_average_crossover(data):
    closes = [c["close"] for c in data]
    if len(closes) < 50:
        return "hold"
    short_ma = np.mean(closes[-10:])
    long_ma = np.mean(closes[-50:])
    return "buy" if short_ma > long_ma else "sell"

def choose_strategy(tendency, direction, data):
    # Neue Logik:
    # Bei "trend": 
    #   up -> buy, down -> sell
    # Bei "sideways":
    #   up -> buy, down -> sell, flat -> hold
    # Bei "unknown": hold
    if tendency == "trend":
        if direction == "up":
            return "buy"
        elif direction == "down":
            return "sell"
        else:
            return "hold"
    elif tendency == "sideways":
        if direction == "up":
            return "buy"
        elif direction == "down":
            return "sell"
        else:
            return "hold"
    else:
        # unknown
        return "hold"
