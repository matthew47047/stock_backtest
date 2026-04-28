from __future__ import annotations

from typing import Dict, List

from backtester import Backtester
from market_data import fetch_history, fetch_latest_price, normalize_tw_ticker
from strategy_example import moving_average_signal


def run_equal_weight_portfolio(
    tickers: List[str],
    start: str,
    end: str,
    total_capital: float,
    short_window: int,
    long_window: int,
) -> Dict[str, object]:
    if not tickers:
        raise ValueError("至少要提供一檔股票")

    normalized = [normalize_tw_ticker(t) for t in tickers]
    capital_per_stock = total_capital / len(normalized)

    per_stock: Dict[str, Dict[str, object]] = {}
    total_final_assets = 0.0
    total_current_stock_value = 0.0
    total_current_bank_balance = 0.0

    for ticker in normalized:
        data = fetch_history(ticker, start, end)
        signal = moving_average_signal(data, short_window, long_window)
        backtester = Backtester(initial_capital=capital_per_stock)
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
        "capital_per_stock": capital_per_stock,
        "per_stock": per_stock,
        "portfolio_final_assets": total_final_assets,
        "portfolio_return": portfolio_return,
        "portfolio_current_stock_value": total_current_stock_value,
        "portfolio_current_bank_balance": total_current_bank_balance,
        "portfolio_current_total_assets": total_current_stock_value + total_current_bank_balance,
    }
