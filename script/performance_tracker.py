# performance_tracker.py
class PerformanceTracker:
    def __init__(self):
        self.total_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.total_profit_loss = 0.0

    def log_trade(self, profit_loss: float):
        self.total_trades += 1
        self.total_profit_loss += profit_loss
        if profit_loss > 0:
            self.successful_trades += 1
        else:
            self.failed_trades += 1

    def summary(self) -> dict:
        success_rate = (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        return {
            "Total Trades": self.total_trades,
            "Successful Trades": self.successful_trades,
            "Failed Trades": self.failed_trades,
            "Total Profit/Loss": self.total_profit_loss,
            "Success Rate (%)": success_rate
        }
