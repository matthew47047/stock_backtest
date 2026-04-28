from __future__ import annotations

from typing import Dict, List, Optional

from backtester import Backtester
from market_data import fetch_history, fetch_latest_price, normalize_tw_ticker
from strategy_example import moving_average_signal


def _normalize_weights(
    tickers: List[str],
    weights: Optional[List[float]],
) -> Dict[str, float]:
    if weights is None:
        equal_weight = 1.0 / len(tickers)
        return {ticker: equal_weight for ticker in tickers}

    if len(weights) != len(tickers):
        raise ValueError("weights 長度必須與 tickers 一致")

    if any(w < 0 for w in weights):
        raise ValueError("weights 不可為負數")

    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("weights 總和必須大於 0")

    return {ticker: weight / total_weight for ticker, weight in zip(tickers, weights)}


def run_portfolio(
    tickers: List[str],
    start: str,
    end: str,
    total_capital: float,
    short_window: int,
    long_window: int,
    weights: Optional[List[float]] = None,
) -> Dict[str, object]:
    if not tickers:
        raise ValueError("至少要提供一檔股票")

    normalized = [normalize_tw_ticker(t) for t in tickers]
    normalized_weights = _normalize_weights(normalized, weights)

    per_stock: Dict[str, Dict[str, object]] = {}
    total_final_assets = 0.0
    total_current_stock_value = 0.0
    total_current_bank_balance = 0.0

    for ticker in normalized:
        allocated_capital = total_capital * normalized_weights[ticker]
        data = fetch_history(ticker, start, end)
        signal = moving_average_signal(data, short_window, long_window)
        backtester = Backtester(initial_capital=allocated_capital)
        result = backtester.run(data, signal)

        latest_price = fetch_latest_price(ticker)
        final_shares = int(result["history"]["shares"].iloc[-1])
        current_stock_value = final_shares * latest_price
        current_bank_balance = float(result["final_bank_balance"])
        current_total_assets = current_stock_value + current_bank_balance

        total_final_assets += float(result["final_total_assets"])
        total_current_stock_value += current_stock_value
        total_current_bank_balance += current_bank_balance

        per_stock[ticker] = {
            "weight": normalized_weights[ticker],
            "allocated_capital": allocated_capital,
            "final_total_assets": float(result["final_total_assets"]),
            "total_return": float(result["total_return"]),
            "latest_price": latest_price,
            "final_shares": final_shares,
            "current_stock_value": current_stock_value,
            "current_bank_balance": current_bank_balance,
            "current_total_assets": current_total_assets,
        }

    portfolio_return = (total_final_assets - total_capital) / total_capital

    return {
        "tickers": normalized,
        "weights": normalized_weights,
        "per_stock": per_stock,
        "portfolio_final_assets": total_final_assets,
        "portfolio_return": portfolio_return,
        "portfolio_current_stock_value": total_current_stock_value,
        "portfolio_current_bank_balance": total_current_bank_balance,
        "portfolio_current_total_assets": total_current_stock_value + total_current_bank_balance,
    }


def run_equal_weight_portfolio(
    tickers: List[str],
    start: str,
    end: str,
    total_capital: float,
    short_window: int,
    long_window: int,
) -> Dict[str, object]:
    return run_portfolio(
        tickers=tickers,
        start=start,
        end=end,
        total_capital=total_capital,
        short_window=short_window,
        long_window=long_window,
        weights=None,
    )
