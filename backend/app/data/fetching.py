from __future__ import annotations
import os
import time
import io
import sys
import tempfile
import traceback
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pytz
from datetime import datetime, timedelta, date

from app.core.config import (
    CLOSING_DATA_PATH,
    TIMEZONE,
    YFINANCE_THREADS,
    RETRY_TOTAL,
    RETRY_BACKOFF,
    CSV_DIR,
)

# Use your provided symbol universe here (trim duplicates)
SYMBOLS = [
'RELIANCE.NS','HDFCBANK.NS','TCS.NS','INFY.NS','HCLTECH.NS','ITC.NS','SBIN.NS','ICICIBANK.NS','HINDUNILVR.NS','KOTAKBANK.NS',
'AXISBANK.NS','LT.NS','BHARTIARTL.NS','BAJAJFINSV.NS','ASIANPAINT.NS','HDFC.NS','MARUTI.NS','SUNPHARMA.NS','POWERGRID.NS','TECHM.NS',
'EICHERMOT.NS','DIVISLAB.NS','WIPRO.NS','UPL.NS','HINDALCO.NS','TITAN.NS','JSWSTEEL.NS','ADANIPORTS.NS','ONGC.NS','COALINDIA.NS',
'NTPC.NS','GRASIM.NS','BPCL.NS','INDUSINDBK.NS','ADANIENT.NS','BRITANNIA.NS','DRREDDY.NS','GAIL.NS','PIDILITIND.NS','HAVELLS.NS',
'DABUR.NS','TATAMOTORS.NS','BAJAJAUTO.NS','HINDZINC.NS','LTI.NS','ADANIGREEN.NS','SRF.NS','AMBUJACEM.NS','UBL.NS','COLPAL.NS',
'M&M.NS','HEROMOTOCO.NS','SHREECEM.NS','GODREJCP.NS','HDFCLIFE.NS','SIEMENS.NS','CIPLA.NS','BANKBARODA.NS','ABB.NS','TVSMOTOR.NS',
'LTIMINDTR.NS','CANBK.NS','ADANITRANS.NS','BAJFINANCE.NS','ZEEL.NS','LICI.NS','MOTHERSON.NS','INDIGOPN.NS','TORNTPHARM.NS','PNB.NS',
'HINDPETRO.NS','GODREJAGRO.NS','BOSCHLTD.NS','NAUKRI.NS','SRTRANSFIN.NS','EXIDEIND.NS','SUNTV.NS','TRENT.NS','GMRINFRA.NS','JINDALSTEL.NS',
'ADANITOTAL.NS','JAICORPLTD.NS','ATGL.NS','MCDOWELL-N.NS','ALKYLAMINE.NS','BAJAJHLDNG.NS','VEDANTA.NS',
'GODREJPROP.NS','DHFL.NS','AMARAJABAT.NS','TATAELXSI.NS','PFC.NS','BHEL.NS','JUBLFOOD.NS'
]

# remove duplicates while preserving order
_seen = set()
SYMBOLS = [s for s in SYMBOLS if not (s in _seen or _seen.add(s))]

# ---------- helper: http session with retries (for any HTTP calls) ----------
def create_retry_session(total: int = RETRY_TOTAL, backoff_factor: float = RETRY_BACKOFF) -> requests.Session:
    s = requests.Session()
    retries = Retry(total=total, backoff_factor=backoff_factor,
                    status_forcelist=(429, 500, 502, 503, 504),
                    allowed_methods=frozenset(['GET','POST']))
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

_http_session = create_retry_session()

# ---------- Data fetcher ----------
def fetch_eod_for_symbols(symbols: List[str], start: str = None, end: str = None, threads: int = YFINANCE_THREADS) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    date (datetime), open, high, low, close, volume, symbol
    Uses yfinance multi-download and falls back per-symbol if a group fetch fails.
    """
    if not symbols:
        return pd.DataFrame()

    print(f"[{datetime.utcnow().isoformat()}] Fetching data for {len(symbols)} symbols with yfinance (threads={threads})...")
    try:
        raw = yf.download(
            tickers=symbols,
            start=start,
            end=end,
            interval='1d',
            group_by='ticker',
            threads=True if threads > 1 else False,
            auto_adjust=True,
            progress=False
        )
    except Exception as e:
        print("Warning: yfinance group download failed, will fallback to per-symbol fetch. Error:", e)
        raw = None

    records = []
    if isinstance(raw, pd.DataFrame) and isinstance(raw.columns, pd.MultiIndex):
        # multi-ticker response
        for sym in symbols:
            try:
                df_sym = raw[sym].copy().reset_index()
                df_sym['symbol'] = sym
                df_sym.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}, inplace=True)
                records.append(df_sym[['date','open','high','low','close','volume','symbol']])
            except Exception:
                # missing symbol in multi response
                continue
    else:
        # fallback: per-symbol download (more robust but slower)
        for sym in symbols:
            try:
                df_sym = yf.download(sym, start=start, end=end, interval='1d', auto_adjust=True, progress=False)
                if df_sym is None or df_sym.empty:
                    print(f" - no data for {sym}")
                    continue
                df_sym = df_sym.reset_index()
                df_sym['symbol'] = sym
                df_sym.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}, inplace=True)
                records.append(df_sym[['date','open','high','low','close','volume','symbol']])
            except Exception as e:
                print(f"Error fetching {sym}: {e}")
                continue

    if not records:
        print("No data retrieved for any symbols.")
        return pd.DataFrame()

    df_all = pd.concat(records, ignore_index=True)
    df_all.sort_values(['symbol','date'], inplace=True)
    # normalize date column to date only (no timezone)
    df_all['date'] = pd.to_datetime(df_all['date']).dt.date
    # ensure columns exist and correct types
    cols = ['symbol','date','open','high','low','close','volume']
    for c in cols:
        if c not in df_all.columns:
            df_all[c] = pd.NA
    df_all = df_all[cols]
    return df_all

# ---------- safe atomic CSV write ----------
def atomic_write_csv(df: pd.DataFrame, path: str):
    # write to temp file then atomically replace
    fd, tmp_path = tempfile.mkstemp(prefix="tmp_all_data_", dir=CSV_DIR, text=True)
    os.close(fd)
    try:
        df.to_csv(tmp_path, index=False)
        # use os.replace to atomically move on most OSes
        os.replace(tmp_path, path)
        print(f"[{datetime.utcnow().isoformat()}] Wrote CSV to {path} (rows={len(df)})")
    except Exception:
        # cleanup on error
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise

# ---------- orchestrator: compute start/end date and run fetch+save ----------
def update_all_data(csv_path: str = CLOSING_DATA_PATH):
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    # We want the most recent EOD. Use end = today+1 to ensure yfinance returns today's row (if available).
    end_dt = now.date() + timedelta(days=1)
    # Start: keep 365 days history by default (you can change)
    start_dt = now.date() - timedelta(days=365)
    start_str = start_dt.isoformat()
    end_str = end_dt.isoformat()
    print(f"[{datetime.utcnow().isoformat()}] Starting update job. range={start_str} -> {end_str}")

    try:
        df_all = fetch_eod_for_symbols(SYMBOLS, start=start_str, end=end_str, threads=YFINANCE_THREADS)
        if df_all.empty:
            print("No data fetched; skipping CSV write.")
            return {"status":"no_data", "updated":0}
        # Save the CSV atomically
        atomic_write_csv(df_all, csv_path)
        return {"status":"ok", "updated": len(df_all), "date": str(end_dt - timedelta(days=1))}
    except Exception as e:
        print("Exception during update_all_data:", e)
        traceback.print_exc()
        return {"status":"error", "error": str(e)}