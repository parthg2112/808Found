# put yfinance v2 code here

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Any

# ================== CONFIG ==================
CONFIG: Dict[str, Any] = {
    'short_ma_period': 10,
    'short_ma_type': 'EMA',
    'long_ma_period': 50,
    'long_ma_type': 'SMA',
    'stop_loss_pct': 5.0,
    'take_profit_pct': 10.0,
    'position_size': 100,
    'initial_capital': 100000,

    # Yahoo Finance setup
    'symbols': [
        # --- Large Cap Tech ---
        'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',

        # --- Banking & Financials ---
        'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',

        # --- Energy & Commodities ---
        'RELIANCE.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS', 'POWERGRID.NS',

        # --- FMCG & Consumer ---
        'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'DABUR.NS', 'BRITANNIA.NS',

        # --- Pharma & Healthcare ---
        'SUNPHARMA.NS', 'CIPLA.NS', 'DRREDDY.NS', 'DIVISLAB.NS', 'LUPIN.NS',

        # --- Auto & Industrial ---
        'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'M&M.NS', 'HEROMOTOCO.NS',

        # --- Infrastructure & Cement ---
        'ULTRACEMCO.NS', 'GRASIM.NS', 'AMBUJACEM.NS', 'SHREECEM.NS', 'L&T.NS',
    ],

    'start_date': '2025-07-01',
    'end_date': '2025-11-01',
    'data_source': 'yfinance',

    'trade_log_path': 'trade_log.csv',
    'summary_path': 'backtest_summary.csv',

    'enable_commission': False,
    'enable_slippage': False,
    'enable_trend_filter': True,
    'enable_volume_filter': True,
    'enable_risk_sizing': False,
}

# ================== LOAD DATA ==================
def load_data(config: Dict[str, Any]) -> pd.DataFrame:
    symbols = config.get('symbols')
    start = config.get('start_date', '2024-01-01')
    end = config.get('end_date', None)

    print(f"Fetching data from Yahoo Finance for {len(symbols)} symbols...")
    data = yf.download(
        tickers=symbols,
        start=start,
        end=end,
        interval='1d',
        group_by='ticker',
        threads=True,
        auto_adjust=True
    )

    records = []
    for sym in symbols:
        try:
            df_sym = data[sym].reset_index()
            df_sym['symbol'] = sym
            df_sym.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            records.append(df_sym)
        except Exception as e:
            print(f"⚠️ Skipping {sym} due to error: {e}")

    df = pd.concat(records, ignore_index=True)
    print(f"✅ Fetched {len(df)} rows of data for {len(records)} symbols successfully.")
    return df

# ================== STRATEGY ==================
def compute_indicators(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    df = df.copy()
    short_period = config['short_ma_period']
    long_period = config['long_ma_period']

    if config['short_ma_type'].upper() == 'EMA':
        df['short_ma'] = df['close'].ewm(span=short_period, adjust=False).mean()
    else:
        df['short_ma'] = df['close'].rolling(short_period).mean()

    if config['long_ma_type'].upper() == 'EMA':
        df['long_ma'] = df['close'].ewm(span=long_period, adjust=False).mean()
    else:
        df['long_ma'] = df['close'].rolling(long_period).mean()

    return df

# ================== SIGNAL GENERATION ==================
def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
    return df

# ================== BACKTESTING LOGIC ==================
def backtest(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    position_size = config['position_size']
    initial_capital = config['initial_capital']

    capital = initial_capital
    position = 0
    entry_price = 0
    trade_log = []

    for i in range(1, len(df)):
        signal = df.loc[i, 'signal']
        price = df.loc[i, 'close']
        date = df.loc[i, 'date']

        if signal == 1 and position == 0:
            position = position_size
            entry_price = price
            trade_log.append({'date': date, 'action': 'BUY', 'price': price, 'capital': capital})

        elif signal == -1 and position > 0:
            profit = (price - entry_price) * position
            capital += profit
            trade_log.append({'date': date, 'action': 'SELL', 'price': price, 'capital': capital})
            position = 0

    df_trades = pd.DataFrame(trade_log)
    if not df_trades.empty:
        df_trades.to_csv(config['trade_log_path'], index=False)
        print(f"💾 Trade log saved to {config['trade_log_path']}")

    pnl = capital - initial_capital
    roi = (pnl / initial_capital) * 100

    summary = {
        'Initial Capital': initial_capital,
        'Final Capital': capital,
        'PnL': pnl,
        'ROI (%)': roi,
        'Total Trades': len(df_trades) if not df_trades.empty else 0,
    }

    pd.DataFrame([summary]).to_csv(config['summary_path'], index=False)
    print(f"📊 Summary saved to {config['summary_path']}")
    return summary

# ================== MAIN ==================
def main():
    config = CONFIG
    df = load_data(config)
    summary_all = []

    for symbol in config['symbols']:
        df_sym = df[df['symbol'] == symbol].reset_index(drop=True)
        if df_sym.empty:
            print(f"⚠️ No data for {symbol}, skipping.")
            continue

        df_sym = compute_indicators(df_sym, config)
        df_sym = generate_signals(df_sym)
        print(f"\n🚀 Running backtest for {symbol}...")
        result = backtest(df_sym, config)
        result['Symbol'] = symbol
        summary_all.append(result)

    summary_df = pd.DataFrame(summary_all)
    print("\n=== 🧾 BACKTEST SUMMARY ===")
    print(summary_df)

if __name__ == "__main__":
    main()
