from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class DailySnapshot:
    date: pd.Timestamp
    close_price: float
    shares: int
    bank_balance: float
    stock_value: float
    total_assets: float
    action: str


class Backtester:
    def __init__(
        self,
        initial_capital: float,
        trade_fee_rate: float = 0.001425,
        tax_rate_on_sell: float = 0.003,
    ) -> None:
        self.initial_capital = initial_capital
        self.trade_fee_rate = trade_fee_rate
        self.tax_rate_on_sell = tax_rate_on_sell

    def run(
        self,
        data: pd.DataFrame,
        signal: pd.Series,
    ) -> Dict[str, object]:
        if "Close" not in data.columns:
            raise ValueError("data 必須包含 Close 欄位")
        if len(data) != len(signal):
            raise ValueError("data 與 signal 長度必須一致")

        bank_balance = float(self.initial_capital)
        shares = 0
        snapshots: List[DailySnapshot] = []

        for date, row in data.iterrows():
            close_price = float(row["Close"])
            desired_hold = int(signal.loc[date]) == 1
            action = "HOLD"

            if desired_hold and shares == 0:
                # 全倉買入，保留不足一股的餘額在銀行
                max_lots = int(bank_balance // (close_price * (1 + self.trade_fee_rate)))
                if max_lots > 0:
                    buy_cost = max_lots * close_price
                    buy_fee = buy_cost * self.trade_fee_rate
                    bank_balance -= buy_cost + buy_fee
                    shares = max_lots
                    action = "BUY"

            elif (not desired_hold) and shares > 0:
                sell_value = shares * close_price
                sell_fee = sell_value * self.trade_fee_rate
                sell_tax = sell_value * self.tax_rate_on_sell
                bank_balance += sell_value - sell_fee - sell_tax
                shares = 0
                action = "SELL"

            stock_value = shares * close_price
            total_assets = bank_balance + stock_value
            snapshots.append(
                DailySnapshot(
                    date=date,
                    close_price=close_price,
                    shares=shares,
                    bank_balance=bank_balance,
                    stock_value=stock_value,
                    total_assets=total_assets,
                    action=action,
                )
            )

        history = pd.DataFrame([s.__dict__ for s in snapshots]).set_index("date")
        final_total_assets = float(history["total_assets"].iloc[-1])
        total_return = (final_total_assets - self.initial_capital) / self.initial_capital

        return {
            "history": history,
            "final_bank_balance": float(history["bank_balance"].iloc[-1]),
            "final_stock_value": float(history["stock_value"].iloc[-1]),
            "final_total_assets": final_total_assets,
            "total_return": total_return,
        }
