import os

# --- PATHS ---
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "csv")
CLOSING_DATA_PATH = os.path.join(CSV_DIR, "closing_data.csv")
TRADE_LOG_PATH = os.path.join(CSV_DIR, "trade_log.csv")
BACKTEST_SUMMARY_PATH = os.path.join(CSV_DIR, "backtest_summary.csv")

# --- SCHEDULER ---
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", "16"))
SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", "0"))

# --- YFINANCE ---
YFINANCE_THREADS = int(os.getenv("YFINANCE_THREADS", "6"))
RETRY_TOTAL = int(os.getenv("HTTP_RETRY_TOTAL", "5"))
RETRY_BACKOFF = float(os.getenv("HTTP_BACKOFF", "1.0"))
