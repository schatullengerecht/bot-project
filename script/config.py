# config.py

XTB_API_URL = "wss://ws.xtb.com/demo"
USER_ID = "17151753"       # Benutzername
PASSWORD = "30Access09#"   # Passwort

# Märkte
MARKETS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD",
    "EURGBP", "EURJPY", "NZDUSD", "USDCHF", "CARDANO",
    "DE40", "US500", "RIPPLE", "BITCOIN", "ETHEREUM"
]

# Risikomanagement und Intervalle
MAX_RISK_PERCENTAGE = 0.005       # Max. 0,5% des Eigenkapitals pro Trade
TAKE_PROFIT_MULTIPLIER = 2        # TP = 2x Risiko
TRAILING_STOP_MULTIPLIER = 1.5    # Trailing-Stop nach 1,5x Risiko
ANALYSIS_INTERVAL = 900           # 15 Minuten in Sekunden
PING_INTERVAL = 30                # Ping alle 30 Sekunden
PING_TIMEOUT = 5                  # Timeout für Ping
LOGIN_TIMEOUT = 10                # Timeout für Login-Vorgang
DATA_TIMEOUT = 15                 # Timeout für Marktdaten
