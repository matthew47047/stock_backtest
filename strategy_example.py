from __future__ import annotations

import pandas as pd


def moving_average_signal(data: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> pd.Series:
    """
    簡單均線策略訊號：
    - 1: 持有/買進
    - 0: 空手/賣出
    """
    close = data["Close"]
    short_ma = close.rolling(short_window).mean()
    long_ma = close.rolling(long_window).mean()

    signal = (short_ma > long_ma).astype(int)
    return signal.fillna(0)
