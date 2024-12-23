# logger.py
import logging

logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_message(level: str, message: str):
    if level.lower() == "info":
        logging.info(message)
    elif level.lower() == "error":
        logging.error(message)
    elif level.lower() == "warning":
        logging.warning(message)
    print(f"{level.upper()}: {message}")
