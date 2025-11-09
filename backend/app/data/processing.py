#!/usr/bin/env python3
"""
MA Crossover Backtester
Author: 808 Found
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

from app.core.config import (
    CLOSING_DATA_PATH,
    TRADE_LOG_PATH,
    BACKTEST_SUMMARY_PATH,
)

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
    'position_size': 100,     # fixed shares (used only when enable_risk_sizing=False)
    'initial_capital': 100000,

    # Universe / dates / data
    'symbols': None,          # None means all symbols in data
    'start_date': '2025-07-01',
    'end_date': None,
    'data_source': CLOSING_DATA_PATH,    # 'demo' or path to CSV

    # Outputs
    'trade_log_path': TRADE_LOG_PATH,
    'summary_path': BACKTEST_SUMMARY_PATH,

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
    'enable_risk_sizing': True,    # Enable smart position sizing based on risk
    'risk_per_trade_pct': 2.0,     # % of capital at risk per trade (2% is realistic)

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
    """Weighted Moving Average with proper edge case handling."""
    if period < 1:
        return pd.Series(np.nan, index=series.index)
    if period == 1:
        return series
    
    weights = np.arange(1, period + 1)
    wma = series.rolling(period).apply(lambda x: (x * weights).sum() / weights.sum(), raw=True)
    return wma

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
    """
    Apply slippage against the trader (conservative):
    - Entry: price increases (trader pays more)
    - Exit: price decreases (trader receives less)
    """
    # This is a conservative model, always applying slippage against the trader.
    if config.get('enable_slippage', False) and config.get('slippage_pct', 0.0) > 0:
        slip = price * (config['slippage_pct'] / 100.0)
        return price + slip if is_entry else price - slip
    return price

def commission_cost(price: float, shares: int, config: Dict[str, Any]) -> float:
    """
    Calculates the commission for a trade.
    The model can include a fixed fee per trade and/or a percentage of the total trade value.
    """
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

def _safe_bars_held(s: pd.DataFrame, exit_date: pd.Timestamp, entry_date: pd.Timestamp) -> int:
    """Safely calculate bars held, handling cases where dates might not align perfectly."""
    try:
        entry_idx = s.index.get_loc(entry_date)
        exit_idx = s.index.get_loc(exit_date)
        return exit_idx - entry_idx
    except KeyError:
        # Fallback for dates not in index: count business days
        return len(pd.bdate_range(start=entry_date, end=exit_date))

# =========================
# SIMULATION / TRADE EXECUTION
# =========================
# =========================
# PORTFOLIO-LEVEL SIMULATION (REPLACEMENT)
# =========================
def simulate_trades(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
    """
    Portfolio-level simulator with proper equity tracking:
      - Single cash pool (initial_capital)
      - Entry at open of day AFTER cross_up (prev day's cross_up == 1)
      - Exit intrabar at stop/tp (low/high) or at open after cross_down
      - Conservative: stop-loss checked before take-profit intrabar
      - Risk sizing uses current cash (not initial capital) for adaptive position sizing
      - Deduct cash at entry; release cash at exit
      - Caps shares to available cash (no leverage)
      
    Returns:
      - trades: List of trade dicts
      - equity_df: DataFrame with daily equity curve (date, cash, pos_value, equity)
    """
    trades: List[Dict[str, Any]] = []
    initial_cap = float(config.get('initial_capital', 100000.0))
    cash = initial_cap
    positions = {}  # symbol -> dict(entry_price, shares, entry_date, entry_comm)
    # prepare per-symbol frames and helper columns
    sym_frames = {}
    for sym in sorted(df['symbol'].unique()):
        s = df[df['symbol'] == sym].copy().sort_values('date').reset_index(drop=True)
        # precompute entry_on_date: True if previous bar had cross_up == 1
        s['entry_on_date'] = s['cross_up'].shift(1).fillna(0).astype(int)
        # precompute signal_exit_on_date: True if previous bar had cross_down == 1 (exit at open)
        s['exit_on_date'] = s['cross_down'].shift(1).fillna(0).astype(int)
        s.set_index('date', inplace=True)
        sym_frames[sym] = s

    # build global set of trading dates (union of dates across symbols), sorted
    all_dates = sorted({d for s in sym_frames.values() for d in s.index})

    # equity series per date
    equity_ts = []

    # track max shares used for diagnostics
    max_shares_used = 0

    for current_date in all_dates:
        # First: process exits for positions that have data on current_date
        # We evaluate intraday (low/high) or signal-based exit at today's open
        syms_with_pos = list(positions.keys())
        for sym in syms_with_pos:
            pos = positions[sym]
            s = sym_frames.get(sym)
            if current_date not in s.index:
                # no market data for this symbol today
                continue
            row = s.loc[current_date]
            low = float(row['low'])
            high = float(row['high'])
            open_p = float(row['open'])
            # compute stop/tp for this position
            if config.get('enable_atr_stop', False) and not np.isnan(row.get('atr', np.nan)):
                atr_at_bar = float(row.get('atr', np.nan))
                stop_price = pos['entry_price'] - config.get('atr_multiplier_sl', 1.5) * atr_at_bar
                take_price = pos['entry_price'] + config.get('atr_multiplier_tp', 3.0) * atr_at_bar
            else:
                stop_price = pos['entry_price'] * (1 - config.get('stop_loss_pct', 5.0) / 100.0)
                take_price = pos['entry_price'] * (1 + config.get('take_profit_pct', 10.0) / 100.0)

            exit_price = None
            exit_reason = None

            # conservative ordering: stop first, then tp, then signal exit at open
            if low <= stop_price:
                exit_price = stop_price
                exit_reason = 'stop_loss'
            elif high >= take_price:
                exit_price = take_price
                exit_reason = 'take_profit'
            elif row.get('exit_on_date', 0) == 1:
                # exit by signal at today's open
                exit_price = apply_slippage(open_p, is_entry=False, config=config)
                exit_reason = 'signal_exit'

            if exit_price is not None:
                # apply slippage if configured (for stop/take we also apply)
                if config.get('enable_slippage', False):
                    exit_price = apply_slippage(exit_price, is_entry=False, config=config)
                exit_comm = commission_cost(exit_price, pos['shares'], config)
                proceeds = exit_price * pos['shares'] - exit_comm
                # update cash
                cash += proceeds
                # compute pnl and record trade
                gross_pnl = (exit_price - pos['entry_price']) * pos['shares']
                total_comm = pos['entry_comm'] + exit_comm
                net_pnl = gross_pnl - total_comm
                pnl_pct = (exit_price - pos['entry_price']) / pos['entry_price'] * 100.0
                trades.append({
                    'symbol': sym,
                    'entry_date': pos['entry_date'],
                    'entry_price': round(pos['entry_price'], 6),
                    'exit_date': current_date,
                    'exit_price': round(exit_price, 6),
                    'shares': int(pos['shares']),
                    'gross_pnl': round(gross_pnl, 6),
                    'commissions': round(total_comm, 6),
                    'net_pnl': round(net_pnl, 6),
                    'pnl_pct': round(pnl_pct, 6),
                    'exit_reason': exit_reason,
                    'bars_held': _safe_bars_held(s, current_date, pos['entry_date'])
                })
                # remove position
                del positions[sym]

        # Second: process entries for symbols where entry_on_date == 1 (and no existing position)
        for sym, s in sym_frames.items():
            if current_date not in s.index:
                continue
            row = s.loc[current_date]
            # entry flag is 1 for dates where previous bar had cross_up
            if int(row.get('entry_on_date', 0)) != 1:
                continue
            if sym in positions:
                continue  # already in position, skip
            # attempt to enter at today's open
            entry_price = apply_slippage(float(row['open']), is_entry=True, config=config)
            # determine desired shares
            if config.get('enable_risk_sizing', False):
                # compute per-share risk
                if config.get('enable_atr_stop', False) and not np.isnan(row.get('atr', np.nan)):
                    atr_at_bar = float(row.get('atr', np.nan))
                    per_share_risk = config.get('atr_multiplier_sl', 1.5) * atr_at_bar
                else:
                    per_share_risk = entry_price * (config.get('stop_loss_pct', 5.0) / 100.0)
                risk_amount = cash * (config.get('risk_per_trade_pct', 1.0) / 100.0)
                if per_share_risk <= 0:
                    desired_shares = int(config.get('position_size', 1))
                else:
                    desired_shares = max(1, int(risk_amount // per_share_risk))
            else:
                desired_shares = int(config.get('position_size', 100))

            # cap shares to available cash (no margin)
            max_affordable = int(np.floor(cash / (entry_price if entry_price > 0 else 1e-9)))
            shares = min(desired_shares, max_affordable)
            if shares <= 0:
                # cannot afford even 1 share; skip entry
                continue

            # compute entry commission and deduct cash
            entry_comm = commission_cost(entry_price, shares, config)
            total_entry_cost = entry_price * shares + entry_comm
            # guard against insufficient cash (with small tolerance for rounding)
            if total_entry_cost > cash + 1e-9:
                continue

            cash -= total_entry_cost
            positions[sym] = {
                'entry_price': entry_price,
                'shares': shares,
                'entry_date': current_date,
                'entry_comm': entry_comm
            }
            max_shares_used = max(max_shares_used, shares)

        # End of day: compute mark-to-market equity (use close price for valuation)
        total_pos_value = 0.0
        for sym, pos in positions.items():
            s = sym_frames.get(sym)
            if current_date in s.index:
                close_p = float(s.loc[current_date]['close'])
            else:
                # use last available close for that symbol (fallback)
                close_p = float(s['close'].ffill().iloc[-1])
            total_pos_value += pos['shares'] * close_p
        equity = cash + total_pos_value
        equity_ts.append({'date': current_date, 'cash': cash, 'pos_value': total_pos_value, 'equity': equity})

    # After looping dates, force-close any remaining positions at their last available close
    if positions:
        for sym, pos in list(positions.items()):
            s = sym_frames.get(sym)
            last_date = s.index[-1]
            last_close = float(s.loc[last_date]['close'])
            exit_price = last_close
            exit_comm = commission_cost(exit_price, pos['shares'], config)
            proceeds = exit_price * pos['shares'] - exit_comm
            cash += proceeds
            gross_pnl = (exit_price - pos['entry_price']) * pos['shares']
            total_comm = pos['entry_comm'] + exit_comm
            net_pnl = gross_pnl - total_comm
            pnl_pct = (exit_price - pos['entry_price']) / pos['entry_price'] * 100.0
            trades.append({
                'symbol': sym,
                'entry_date': pos['entry_date'],
                'entry_price': round(pos['entry_price'], 6),
                'exit_date': last_date,
                'exit_price': round(exit_price, 6),
                'shares': int(pos['shares']),
                'gross_pnl': round(gross_pnl, 6),
                'commissions': round(total_comm, 6),
                'net_pnl': round(net_pnl, 6),
                'pnl_pct': round(pnl_pct, 6),
                'exit_reason': 'eod_force_close',
                'bars_held': (s.index.get_loc(last_date) - s.index.get_loc(pos['entry_date']))
            })
            del positions[sym]
        # final equity record after forced closes
        equity = cash
        equity_ts.append({'date': last_date, 'cash': cash, 'pos_value': 0.0, 'equity': equity})

    # diagnostics: print top winners/losers quickly (caller may inspect)
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    if not trades_df.empty:
        print("\n--- Trade diagnostics ---")
        print("Total trades:", len(trades_df))
        print("Top 5 winners:")
        print(trades_df.sort_values('net_pnl', ascending=False).head(5)[['symbol','entry_date','exit_date','shares','entry_price','exit_price','net_pnl']])
        print("Top 5 losers:")
        print(trades_df.sort_values('net_pnl', ascending=True).head(5)[['symbol','entry_date','exit_date','shares','entry_price','exit_price','net_pnl']])
        print("Max shares in single trade:", trades_df['shares'].max())
        print("-------------------------\n")

    # return trades list and also attach equity time series to df for metrics
    equity_df = pd.DataFrame(equity_ts)
    # ensure sorted
    equity_df.sort_values('date', inplace=True)
    equity_df.reset_index(drop=True, inplace=True)

    return trades, equity_df


# =========================
# METRICS (REPLACEMENT)
# =========================
def calculate_metrics(trades: List[Dict[str, Any]], equity_df: pd.DataFrame | None, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Metrics based on portfolio equity time series (if available). Falls back to trade-based metrics.
    Adds net_profit_pct computed from final equity.
    """
    initial_capital = float(config.get('initial_capital', 100000.0))

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
            'net_profit': 0.0,
            'net_profit_pct': 0.0
        }

    df_trades = pd.DataFrame(trades).sort_values('exit_date').reset_index(drop=True)
    total_trades = len(df_trades)
    wins = df_trades[df_trades['net_pnl'] > 0]
    losses = df_trades[df_trades['net_pnl'] <= 0]
    win_rate = (len(wins) / total_trades * 100.0) if total_trades > 0 else 0.0

    avg_profit_pct = wins['pnl_pct'].mean() if len(wins) > 0 else 0.0
    avg_loss_pct = losses['pnl_pct'].mean() if len(losses) > 0 else 0.0
    max_win = df_trades['net_pnl'].max()
    max_loss = df_trades['net_pnl'].min()
    gross_profit = wins['net_pnl'].sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses['net_pnl'].sum()) if len(losses) > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf

    # compute equity series: try to use attached equity_df from simulate_trades if present
    if equity_df is not None and not equity_df.empty:
        # robust drawdown calc: ensure running_max never below initial_capital
        running_max = equity_df['equity'].cummax().clip(lower=initial_capital)
        drawdown = (equity_df['equity'] - running_max) / running_max * 100.0
        max_drawdown_pct = drawdown.min() if not drawdown.empty else 0.0
        total_return_pct = (equity_df['equity'].iloc[-1] - initial_capital) / initial_capital * 100.0
    else:
        # If no equity_df available, approximate equity at trade exits.
        df_trades['cumulative_net_pnl'] = df_trades['net_pnl'].cumsum()
        df_trades['equity'] = initial_capital + df_trades['cumulative_net_pnl']
        running_max = df_trades['equity'].cummax().clip(lower=initial_capital)
        drawdown = (df_trades['equity'] - running_max) / running_max * 100.0
        max_drawdown_pct = drawdown.min() if not drawdown.empty else 0.0
        total_return_pct = (df_trades['cumulative_net_pnl'].iloc[-1] / initial_capital * 100.0) if not df_trades.empty else 0.0


    # Sharpe: trade returns as pnl / initial capital (decimal), annualized by sqrt(252)
    trade_returns = df_trades['net_pnl'] / initial_capital
    if len(trade_returns) > 1 and trade_returns.std() > 0:
        sharpe = (trade_returns.mean() / trade_returns.std()) * np.sqrt(252.0)
    else:
        sharpe = 0.0

    net_profit = gross_profit - gross_loss
    net_profit_pct = (net_profit / initial_capital) * 100.0 if initial_capital != 0 else 0.0

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
        'net_profit': round(net_profit, 6),
        'net_profit_pct': round(net_profit_pct, 6)
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
    trades, equity_df = simulate_trades(sig_df, config)
    metrics = calculate_metrics(trades, equity_df, config)
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
    trades, equity_df = simulate_trades(sig, config)
    metrics = calculate_metrics(trades, equity_df, config)

    trade_log_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    if not trade_log_df.empty:
        trade_log_df.to_csv(config.get('trade_log_path', 'trade_log.csv'), index=False)
        print(f"Trade log saved to {config.get('trade_log_path')}")
    pd.DataFrame([metrics]).to_csv(config.get('summary_path', 'backtest_summary.csv'), index=False)
    print(f"Summary saved to {config.get('summary_path')}")

    return trade_log_df, metrics, equity_df

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

