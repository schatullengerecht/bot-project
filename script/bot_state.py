# bot_state.py
class BotState:
    _state = {
        "connected": False,
        "session_id": None,
        "trading_active": False,
        "markets": {},
        "open_trades": [],
        "performance": {},
        "markets_to_watch": [
            "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD",
            "EURGBP", "EURJPY", "NZDUSD", "USDCHF", "CARDANO",
            "DE40", "US500", "RIPPLE", "BITCOIN", "ETHEREUM"
        ],
        "signals": [],
        "positions": {}  # Neu: hier speichern wir offene Positionen pro Symbol
    }

    @classmethod
    def get_state(cls):
        return cls._state

    @classmethod
    def set_connected(cls, session_id):
        cls._state["connected"] = True
        cls._state["session_id"] = session_id

    @classmethod
    def disconnect(cls):
        cls._state["connected"] = False
        cls._state["session_id"] = None

    @classmethod
    def start_trading(cls):
        cls._state["trading_active"] = True

    @classmethod
    def stop_trading(cls):
        cls._state["trading_active"] = False

    @classmethod
    def update_markets(cls, market_data: dict):
        cls._state["markets"] = market_data

    @classmethod
    def update_open_trades(cls, trades: list):
        cls._state["open_trades"] = trades
        # Aktualisiere positions basierend auf open_trades
        positions = {}
        for t in trades:
            # Annehmen: t["cmd"] = 0 für buy (long), 1 für sell (short)
            cmd = t.get("cmd", None)
            if cmd is not None:
                if cmd == 0:
                    positions[t["symbol"]] = "long"
                elif cmd == 1:
                    positions[t["symbol"]] = "short"
        cls._state["positions"] = positions

    @classmethod
    def update_performance(cls, perf: dict):
        cls._state["performance"] = perf

