# server.py
from flask import Flask, request, jsonify
from bot_state import BotState
from main import start_bot, stop_bot
from flask import send_from_directory
import os

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def get_status():
    # Gibt den vollständigen State zurueck, inkl. markets und signals
    # markets enthalten tendency und direction, signals enthalten die Kauf-/Verkaufssignale
    return jsonify(BotState.get_state())

@app.route("/start_bot", methods=["POST"])
def start_bot_route():
    start_bot()
    return jsonify({"message": "Bot start initiated"})

@app.route("/stop_bot", methods=["POST"])
def stop_bot_route():
    stop_bot()
    return jsonify({"message": "Bot stopped"})

@app.route("/start_trading", methods=["POST"])
def start_trading():
    BotState.start_trading()
    return jsonify({"message": "Trading started"})

@app.route("/stop_trading", methods=["POST"])
def stop_trading():
    BotState.stop_trading()
    return jsonify({"message": "Trading stopped"})

@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists("trading_bot.log"):
        return jsonify({"logs": []})
    with open("trading_bot.log", "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return jsonify({"logs": lines[-50:]})

@app.route("/signals", methods=["GET"])
def get_signals():
    # Liefert die aufgezeichneten Kauf-/Verkaufssignale zurück
    signals = BotState.get_state().get("signals", [])
    return jsonify({"signals": signals})

@app.route("/")
def index():
    # Liefert die index.html aus dem frontend-Verzeichnis zurück
    return send_from_directory(os.path.join(os.getcwd(), '../frontend'), "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
