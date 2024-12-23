import yfinance as yf

# Zeitrahmen anpassen (beispielhaft 5 Jahre: 01.01.2018 bis 31.12.2023)
start_date = "2018-01-01"
end_date = "2023-12-31"

# Daten von EUR/USD herunterladen (EURUSD=X ist das Yahoo Ticker Symbol)
data = yf.download("EURUSD=X", start=start_date, end=end_date)

# Erste Zeilen ausgeben, um zu prüfen ob es geklappt hat
print(data.head())

# Optional: Daten als CSV speichern
data.to_csv("eurusd_data.csv")
