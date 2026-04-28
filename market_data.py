from __future__ import annotations

import pandas as pd
import yfinance as yf


def normalize_tw_ticker(ticker: str) -> str:
    """
    將台股代號標準化為 yfinance 代號:
    - 上市: 2330 -> 2330.TW
    - 上櫃: 6488 -> 6488.TWO
    若已帶後綴則原樣返回。
    """
    ticker = ticker.strip().upper()
    if ticker.endswith(".TW") or ticker.endswith(".TWO"):
        return ticker

    # 預設使用上市 .TW，若抓不到可手動改成 .TWO
    return f"{ticker}.TW"


def fetch_history(ticker: str, start: str, end: str) -> pd.DataFrame:
    yf_ticker = normalize_tw_ticker(ticker)
    data = yf.download(yf_ticker, start=start, end=end, auto_adjust=False, progress=False)
    if data.empty:
        raise ValueError(f"抓不到資料: {yf_ticker}，請確認代號或日期範圍")

    # yfinance 在某些版本/參數下會回 MultiIndex 欄位，這裡統一攤平成 OHLCV。
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 統一索引與欄位
    data.index = pd.to_datetime(data.index)
    data = data[["Open", "High", "Low", "Close", "Volume"]].dropna()
    return data


def fetch_latest_price(ticker: str) -> float:
    yf_ticker = normalize_tw_ticker(ticker)
    t = yf.Ticker(yf_ticker)
    info = t.fast_info
    last_price = info.get("last_price")
    if last_price is None:
        # 備援：抓最近5天最後收盤
        hist = t.history(period="5d")
        if hist.empty:
            raise ValueError(f"抓不到即時/近期價格: {yf_ticker}")
        last_price = float(hist["Close"].iloc[-1])
    return float(last_price)
