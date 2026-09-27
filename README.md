# 808Found

Stock backtesting platform: a FastAPI backend that fetches NSE stock data and runs moving-average crossover backtests, paired with a Next.js dashboard for configuration, results, and portfolio views.

## Features

- MA crossover backtesting engine supporting SMA/EMA/WMA, ATR-based stops, trend and volume filters, commission/slippage modeling, and risk-based position sizing
- OOS-aware grid search for parameter optimization, exporting trade log and summary CSVs
- Stock data fetching via yfinance (Nifty 500 universe) with APScheduler-driven daily updates
- Synchronous and background backtest endpoints with task status polling
- CSV upload and stock listing endpoints
- Next.js dashboard with Google sign-in (NextAuth), strategy configuration panel, data upload, and results views

## Tech Stack

Backend: Python, FastAPI, uvicorn, pandas, numpy, yfinance, APScheduler, pydantic

Frontend: Next.js, React, TypeScript, NextAuth, Tailwind CSS, Radix UI/shadcn/ui, Recharts, Framer Motion

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Optional environment variables (see `app/core/config.py`):
`TIMEZONE` (default `Asia/Kolkata`), `SCHEDULE_HOUR` (16), `SCHEDULE_MINUTE` (0), `YFINANCE_THREADS` (6), `HTTP_RETRY_TOTAL` (5), `HTTP_BACKOFF` (1.0).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Requires environment variables for NextAuth Google sign-in:
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.
