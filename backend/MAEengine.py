#!/usr/bin/env python3
"""
MA Crossover Backtester - Improved & Configurable
Author: 808 Found (improved)
Date: 2025-11-09

Features:
- SMA/EMA/WMA MAs
- Optional ATR-based stops (and ATR TP)
- Trend & volume filters
- Optional commission & slippage
- Optional risk-based position sizing (toggle)
- OOS-aware grid search for parameter optimization
- Exports trade log and summary CSVs

Default behavior preserves your original assumptions:
- Slippage = 0, commission = 0
- Fixed shares per trade
- Single long position per symbol
- Stop-loss checked before take-profit intrabar (conservative)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Any
import warnings
from pathlib import Path
import itertools
import json

warnings.filterwarnings('ignore')

# =========================
# USER CONFIGURATION
# =========================
CONFIG: Dict[str, Any] = {
    # MA params
    'short_ma_period': 10,
    'short_ma_type': 'EMA',   # 'SMA', 'EMA', 'WMA'
    'long_ma_period': 50,
    'long_ma_type': 'SMA',

    # Risk & sizing
    'stop_loss_pct': 5.0,     # used only if enable_atr_stop is False
    'take_profit_pct': 10.0,  # used only if enable_atr_stop is False
    'position_size': 100,     # fixed shares (default behavior)
    'initial_capital': 100000,

    # Universe / dates / data
    'symbols': None,          # None means all symbols in data
    'start_date': '2025-07-01',
    'end_date': None,
    'data_source': 'nifty500.csv',    # 'demo' or path to CSV

    # Outputs
    'trade_log_path': 'trade_log.csv',
    'summary_path': 'backtest_summary.csv',

    # Realism toggles
    'enable_commission': False,
    'commission_per_trade': 1.0,
    'commission_pct': 0.0,

    'enable_slippage': False,
    'slippage_pct': 0.0,      # percent of price applied against trader

    # ATR-based stops
    'enable_atr_stop': False,
    'atr_period': 14,
    'atr_multiplier_sl': 1.5,
    'atr_multiplier_tp': 3.0,

    # Filters
    'enable_trend_filter': True,   # require both MA slopes > 0
    'enable_volume_filter': True,  # require volume > rolling mean

    # Risk sizing toggle (keeps default fixed shares if False)
    'enable_risk_sizing': False,
    'risk_per_trade_pct': 1.0,     # % of capital at risk

    # Optimization / OOS
    'oos_split_date': None,        # e.g., '2023-01-01' to split train/test; None means no OOS
    'optimize_output_path': 'optimization_results.json',
}

# =========================
# UTILITIES / MA FUNCTIONS
# =========================
def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def calculate_wma(series: pd.Series, period: int) -> pd.Series:
    weights = np.arange(1, period + 1)
    def wma_calc(x):
        return np.dot(x, weights) / weights.sum()
    return series.rolling(window=period, min_periods=period).apply(lambda x: wma_calc(x[-period:]), raw=True)

def calculate_ma(series: pd.Series, period: int, ma_type: str) -> pd.Series:
    t = ma_type.upper()
    if t == 'SMA':
        return calculate_sma(series, period)
    if t == 'EMA':
        return calculate_ema(series, period)
    if t == 'WMA':
        return calculate_wma(series, period)
    raise ValueError(f"Unknown MA type: {ma_type}")

# =========================
# ATR & Helpers
# =========================
def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df['high'] - df['low']
    high_prev = (df['high'] - df['close'].shift(1)).abs()
    low_prev = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)
    atr = tr.rolling(period, min_periods=period).mean()
    return atr

def apply_slippage(price: float, is_entry: bool, config: Dict[str, Any]) -> float:
    if config.get('enable_slippage', False) and config.get('slippage_pct', 0.0) > 0:
        slip = price * (config['slippage_pct'] / 100.0)
        return price + slip if is_entry else price - slip
    return price

def commission_cost(price: float, shares: int, config: Dict[str, Any]) -> float:
    cost = 0.0
    if config.get('enable_commission', False):
        cost += config.get('commission_per_trade', 0.0)
        pct = config.get('commission_pct', 0.0)
        if pct > 0:
            cost += abs(price * shares * (pct / 100.0))
    return cost

# =========================
# DATA LOAD / PREPROCESS
# =========================
def load_data(config: Dict[str, Any]) -> pd.DataFrame:
    if config.get('data_source') == 'demo':
        # Demo daily data for a few symbols (fast sanity checks)
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        data = []
        for symbol in symbols:
            base = np.random.uniform(100, 300)
            prices = base + np.cumsum(np.random.randn(len(dates)) * 2)
            for i, dt in enumerate(dates):
                close = float(prices[i])
                data.append({
                    'date': dt,
                    'symbol': symbol,
                    'open': close + np.random.randn() * 0.5,
                    'high': close + abs(np.random.randn()) * 1.0,
                    'low': close - abs(np.random.randn()) * 1.0,
                    'close': close,
                    'volume': int(np.random.uniform(1e6, 1e7))
                })
        return pd.DataFrame(data)
    else:
        df = pd.read_csv(config['data_source'])
        df['date'] = pd.to_datetime(df['date'])
        # Ensure required columns
        required = {'date', 'symbol', 'open', 'high', 'low', 'close', 'volume'}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Data missing required columns. Need: {required}")
        return df

def preprocess_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    if config.get('symbols') is not None:
        df = df[df['symbol'].isin(config['symbols'])]
    if config.get('start_date'):
        df = df[df['date'] >= pd.to_datetime(config['start_date'])]
    if config.get('end_date'):
        df = df[df['date'] <= pd.to_datetime(config['end_date'])]
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
    return df

# =========================
# SIGNAL GENERATION
# =========================
def generate_signals(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    frames = []
    for sym in sorted(df['symbol'].unique()):
        s = df[df['symbol'] == sym].copy().sort_values('date').reset_index(drop=True)

        # Moving averages
        s['short_ma'] = calculate_ma(s['close'], config['short_ma_period'], config['short_ma_type'])
        s['long_ma'] = calculate_ma(s['close'], config['long_ma_period'], config['long_ma_type'])

        # ATR if needed
        if config.get('enable_atr_stop', False):
            s['atr'] = calculate_atr(s, config.get('atr_period', 14))
        else:
            s['atr'] = np.nan

        # Signals: regime and crosses (we use shift to avoid lookahead)
        s['signal'] = (s['short_ma'] > s['long_ma']).astype(int)
        s['cross_up'] = ((s['signal'] == 1) & (s['signal'].shift(1).fillna(0) == 0)).astype(int)
        s['cross_down'] = ((s['signal'] == 0) & (s['signal'].shift(1).fillna(1) == 1)).astype(int)

        # Filters
        if config.get('enable_trend_filter', True):
            s['short_slope_pos'] = s['short_ma'].diff() > 0
            s['long_slope_pos'] = s['long_ma'].diff() > 0
            s['trend_ok'] = s['short_slope_pos'] & s['long_slope_pos']
        else:
            s['trend_ok'] = True

        if config.get('enable_volume_filter', True):
            s['vol_ok'] = s['volume'] > s['volume'].rolling(20, min_periods=1).mean()
        else:
            s['vol_ok'] = True

        # Apply filters to cross_up (entry) only — keep behavior conservative
        s['cross_up'] = np.where((s['cross_up'] == 1) & s['trend_ok'] & s['vol_ok'], 1, 0)

        frames.append(s)
    return pd.concat(frames, ignore_index=True)

# =========================
# SIMULATION / TRADE EXECUTION
# =========================
def simulate_trades(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Simulate trades:
      - Enter at open of bar AFTER cross_up (no lookahead)
      - Exit at open of bar AFTER cross_down OR intrabar SL/TP
      - Stop-loss checked before take-profit if both hit in same bar (conservative)
      - Single position per symbol
      - Intrabar checks use low/high of the exit bar
    Returns:
      - trades: list of trade dicts
      - df: input df (unchanged) for reference
    """
    trades: List[Dict[str, Any]] = []
    initial_cap = float(config.get('initial_capital', 100000.0))

    for sym in sorted(df['symbol'].unique()):
        s = df[df['symbol'] == sym].copy().sort_values('date').reset_index(drop=True)
        in_position = False
        entry_price = None
        entry_date = None
        entry_idx = None
        entry_shares = None

        for i in range(1, len(s)):
            row = s.iloc[i]
            prev = s.iloc[i-1]

            # Entry condition: previous bar had cross_up -> enter at current open
            if (not in_position) and prev.get('cross_up', 0) == 1:
                # Determine raw entry price (open)
                raw_entry = float(row['open'])
                entry_price = apply_slippage(raw_entry, is_entry=True, config=config)
                entry_date = row['date']
                entry_idx = i

                # Determine position size: fixed unless risk sizing is enabled
                if config.get('enable_risk_sizing', False):
                    # use ATR if enabled to compute per-share risk
                    if config.get('enable_atr_stop', False) and not np.isnan(row.get('atr', np.nan)):
                        atr_at_bar = float(row.get('atr', np.nan))
                        per_share_risk = config.get('atr_multiplier_sl', 1.5) * atr_at_bar
                    else:
                        per_share_risk = entry_price * (config.get('stop_loss_pct', 5.0) / 100.0)
                    risk_amount = initial_cap * (config.get('risk_per_trade_pct', 1.0) / 100.0)
                    if per_share_risk <= 0:
                        entry_shares = int(config.get('position_size', 1))
                    else:
                        entry_shares = max(1, int(risk_amount // per_share_risk))
                else:
                    entry_shares = int(config.get('position_size', 100))

                # Deduct entry commission if configured (for accounting in pnl later)
                entry_comm = commission_cost(entry_price, entry_shares, config)
                # We store entry_comm for later subtraction from pnl
                in_position = True
                # store for use on exit
                current_entry_comm = entry_comm
                current_entry_price = entry_price
                current_entry_shares = entry_shares
                # Note: we continue to evaluate exit on same bar if conditions met (intrabar)
                # (we do NOT `continue` immediately)

            # If in position, evaluate exits (intrabar SL/TP or signal-based)
            if in_position:
                # compute stop and take
                if config.get('enable_atr_stop', False) and not np.isnan(row.get('atr', np.nan)):
                    atr_at_bar = float(row.get('atr', np.nan))
                    stop_price = current_entry_price - config.get('atr_multiplier_sl', 1.5) * atr_at_bar
                    take_price = current_entry_price + config.get('atr_multiplier_tp', 3.0) * atr_at_bar
                else:
                    stop_price = current_entry_price * (1 - config.get('stop_loss_pct', 5.0) / 100.0)
                    take_price = current_entry_price * (1 + config.get('take_profit_pct', 10.0) / 100.0)

                exit_price = None
                exit_reason = None

                low = float(row['low'])
                high = float(row['high'])
                open_p = float(row['open'])

                # Conservative ordering: check stop first, then take
                if low <= stop_price:
                    exit_price = stop_price
                    exit_reason = 'stop_loss'
                elif high >= take_price:
                    exit_price = take_price
                    exit_reason = 'take_profit'
                elif prev.get('cross_down', 0) == 1:
                    # Exit at open of current bar (signal exit)
                    exit_price = apply_slippage(open_p, is_entry=False, config=config)
                    exit_reason = 'signal_exit'

                if exit_price is not None:
                    # Apply slippage to exit_price if not applied already (intrabar cases use raw exit_price)
                    # (for stop/take we modeled exact price; we can optionally apply slippage consistently)
                    if exit_reason in ['stop_loss', 'take_profit']:
                        exit_price = apply_slippage(exit_price, is_entry=False, config=config)

                    # Commission cost for exit
                    exit_comm = commission_cost(exit_price, current_entry_shares, config)

                    # Compute pnl: (exit - entry) * shares - commissions
                    gross_pnl = (exit_price - current_entry_price) * current_entry_shares
                    total_comm = current_entry_comm + exit_comm
                    net_pnl = gross_pnl - total_comm

                    pnl_pct = (exit_price - current_entry_price) / current_entry_price * 100.0

                    trades.append({
                        'symbol': sym,
                        'entry_date': entry_date,
                        'entry_price': round(current_entry_price, 6),
                        'exit_date': row['date'],
                        'exit_price': round(exit_price, 6),
                        'shares': int(current_entry_shares),
                        'gross_pnl': round(gross_pnl, 6),
                        'commissions': round(total_comm, 6),
                        'net_pnl': round(net_pnl, 6),
                        'pnl_pct': round(pnl_pct, 6),
                        'exit_reason': exit_reason,
                        'bars_held': i - entry_idx
                    })

                    # Reset position
                    in_position = False
                    entry_price = None
                    entry_date = None
                    entry_idx = None
                    entry_shares = None

    return trades, df

# =========================
# METRICS
# =========================
def calculate_metrics(trades: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate_pct': 0.0,
            'avg_profit_pct': 0.0,
            'avg_loss_pct': 0.0,
            'max_win': 0.0,
            'max_loss': 0.0,
            'profit_factor': 0.0,
            'max_drawdown_pct': 0.0,
            'total_return_pct': 0.0,
            'sharpe_ratio': 0.0,
            'gross_profit': 0.0,
            'gross_loss': 0.0,
            'net_profit': 0.0
        }

    df = pd.DataFrame(trades).sort_values('exit_date').reset_index(drop=True)
    total_trades = len(df)
    wins = df[df['net_pnl'] > 0]
    losses = df[df['net_pnl'] <= 0]
    win_rate = (len(wins) / total_trades * 100.0) if total_trades > 0 else 0.0

    avg_profit_pct = wins['pnl_pct'].mean() if len(wins) > 0 else 0.0
    avg_loss_pct = losses['pnl_pct'].mean() if len(losses) > 0 else 0.0
    max_win = df['net_pnl'].max()
    max_loss = df['net_pnl'].min()
    gross_profit = wins['net_pnl'].sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses['net_pnl'].sum()) if len(losses) > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf

    # equity series at trade exits
    df['cumulative_net_pnl'] = df['net_pnl'].cumsum()
    df['equity'] = config.get('initial_capital', 100000.0) + df['cumulative_net_pnl']
    running_max = df['equity'].cummax()
    drawdown = (df['equity'] - running_max) / running_max * 100.0
    max_drawdown_pct = drawdown.min() if not drawdown.empty else 0.0

    total_return_pct = (df['cumulative_net_pnl'].iloc[-1] / config.get('initial_capital', 100000.0) * 100.0) if not df.empty else 0.0

    # Sharpe: trade returns as pnl / initial capital (decimal), annualized by sqrt(252)
    trade_returns = df['net_pnl'] / float(config.get('initial_capital', 100000.0))
    if len(trade_returns) > 1 and trade_returns.std() > 0:
        sharpe = (trade_returns.mean() / trade_returns.std()) * np.sqrt(252.0)
    else:
        sharpe = 0.0

    return {
        'total_trades': int(total_trades),
        'winning_trades': int(len(wins)),
        'losing_trades': int(len(losses)),
        'win_rate_pct': round(win_rate, 4),
        'avg_profit_pct': round(avg_profit_pct, 6),
        'avg_loss_pct': round(avg_loss_pct, 6),
        'max_win': round(max_win, 6),
        'max_loss': round(max_loss, 6),
        'profit_factor': (round(profit_factor, 6) if profit_factor != np.inf else np.inf),
        'max_drawdown_pct': round(max_drawdown_pct, 6),
        'total_return_pct': round(total_return_pct, 6),
        'sharpe_ratio': round(sharpe, 6),
        'gross_profit': round(gross_profit, 6),
        'gross_loss': round(gross_loss, 6),
        'net_profit': round(gross_profit - gross_loss, 6)
    }

# =========================
# BACKTEST RUNNERS
# =========================
def run_backtest_on_df(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Run signals + simulation on a preloaded DataFrame (useful for OOS splits).
    Returns trades list and metrics dict.
    """
    pre = preprocess_data(df.copy(), config)
    if pre.empty:
        return [], {}
    sig_df = generate_signals(pre, config)
    trades, _ = simulate_trades(sig_df, config)
    metrics = calculate_metrics(trades, config)
    return trades, metrics

def run_backtest(config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    print(">>> Loading data...")
    df = load_data(config)
    print(f"    Rows loaded: {len(df)} | Symbols: {df['symbol'].nunique()}")
    df = preprocess_data(df, config)
    print(f"    After preprocess: {len(df)} rows | Symbols: {df['symbol'].nunique()}")
    if df.empty:
        print("No data after filtering; exiting.")
        return pd.DataFrame(), {}

    print(">>> Generating signals...")
    sig = generate_signals(df, config)

    print(">>> Simulating trades...")
    trades, _ = simulate_trades(sig, config)
    metrics = calculate_metrics(trades, config)

    trade_log_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    if not trade_log_df.empty:
        trade_log_df.to_csv(config.get('trade_log_path', 'trade_log.csv'), index=False)
        print(f"Trade log saved to {config.get('trade_log_path')}")
    pd.DataFrame([metrics]).to_csv(config.get('summary_path', 'backtest_summary.csv'), index=False)
    print(f"Summary saved to {config.get('summary_path')}")

    return trade_log_df, metrics

# =========================
# SIMPLE OOS GRID SEARCH
# =========================
def generate_grid(params: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    keys = list(params.keys())
    combinations = list(itertools.product(*(params[k] for k in keys)))
    grid = [dict(zip(keys, comb)) for comb in combinations]
    return grid

def optimize_with_oos(config: Dict[str, Any], grid_params: Dict[str, List[Any]], split_date: str) -> Dict[str, Any]:
    """
    Performs simple grid search using a train/test split date.
    Returns best candidate by test total_return_pct and writes results to JSON.
    """
    df_all = preprocess_data(load_data(config), config)
    if df_all.empty:
        raise ValueError("No data available to optimize.")

    split_date = pd.to_datetime(split_date)
    train_df = df_all[df_all['date'] <= split_date].copy()
    test_df = df_all[df_all['date'] > split_date].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("Train or Test split resulted in empty set. Choose a different split_date.")

    grid = generate_grid(grid_params)
    records = []
    best = None

    for i, g in enumerate(grid):
        cfg = config.copy()
        cfg.update({
            'short_ma_period': int(g.get('short_ma')),
            'long_ma_period': int(g.get('long_ma')),
            'stop_loss_pct': float(g.get('stop_loss_pct', cfg['stop_loss_pct'])),
            'take_profit_pct': float(g.get('take_profit_pct', cfg['take_profit_pct']))
        })
        # optional: set MA types if provided in grid
        if 'short_ma_type' in g:
            cfg['short_ma_type'] = g['short_ma_type']
        if 'long_ma_type' in g:
            cfg['long_ma_type'] = g['long_ma_type']

        # Train
        trades_train, metrics_train = run_backtest_on_df(train_df, cfg)
        # Test
        trades_test, metrics_test = run_backtest_on_df(test_df, cfg)

        rec = {
            'grid_index': i,
            'params': g,
            'metrics_train': metrics_train,
            'metrics_test': metrics_test
        }
        records.append(rec)

        # choose best by test total_return_pct primarily, fallback to sharpe
        if best is None:
            best = rec
        else:
            current = rec['metrics_test'].get('total_return_pct', -np.inf)
            best_val = best['metrics_test'].get('total_return_pct', -np.inf)
            if current > best_val:
                best = rec

    # Save records
    out_path = config.get('optimize_output_path', 'optimization_results.json')
    with open(out_path, 'w') as f:
        json.dump(records, f, default=str, indent=2)

    print(f"Optimization finished. Results saved to {out_path}")
    return best

# =========================
# CLI / MAIN
# =========================
def print_summary(metrics: Dict[str, Any]):
    if not metrics:
        print("No metrics to show.")
        return
    print("\n=== Backtest Summary ===")
    for k, v in metrics.items():
        print(f"{k:25s} : {v}")
    print("========================\n")

if __name__ == "__main__":
    # Example usage: run backtest and optionally optimization
    cfg = CONFIG.copy()

    # Quick change: if you want to run the demo dataset, it's already set.
    # To run your CSV, set cfg['data_source'] = 'path/to/your.csv'

    # Example: enable ATR stops and risk sizing (optional)
    # cfg['enable_atr_stop'] = True
    # cfg['enable_risk_sizing'] = True
    # cfg['enable_commission'] = True
    # cfg['commission_per_trade'] = 1.0
    # cfg['enable_slippage'] = True
    # cfg['slippage_pct'] = 0.05

    # Run a single backtest
    trades_df, metrics = run_backtest(cfg)
    print_summary(metrics)

    # If you want to run a grid optimization with OOS, uncomment and adjust below:
    # Make sure to set cfg['oos_split_date'] to a valid date present in your data
    # Example parameter grid
    # param_grid = {
    #     'short_ma': [5, 8, 10],
    #     'long_ma': [21, 34, 50],
    #     'stop_loss_pct': [2.0, 4.0, 6.0],
    #     'take_profit_pct': [8.0, 12.0, 16.0]
    # }
    # cfg['oos_split_date'] = '2022-12-31'
    # best = optimize_with_oos(cfg, param_grid, cfg['oos_split_date'])
    # print("Best candidate (by OOS total return):")
    # print(best)
