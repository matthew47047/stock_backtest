from __future__ import annotations

import argparse

from backtester import Backtester
from market_data import fetch_history, fetch_latest_price, normalize_tw_ticker
from portfolio_backtester import run_portfolio
from strategy_example import moving_average_signal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="台股策略回測與資產估值")
    parser.add_argument("--ticker", help="單一台股代號，如 2330 或 2330.TW")
    parser.add_argument("--tickers", help="多檔台股代號，逗號分隔，如 2330,2317,2454")
    parser.add_argument(
        "--weights",
        help="多檔資金權重，逗號分隔，如 0.5,0.3,0.2；若未提供則等權重",
    )
    parser.add_argument("--start", required=True, help="回測起日，格式 YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="回測迄日，格式 YYYY-MM-DD")
    parser.add_argument("--capital", type=float, default=1_000_000, help="啟動資金")
    parser.add_argument("--short-window", type=int, default=5, help="短均線天數")
    parser.add_argument("--long-window", type=int, default=20, help="長均線天數")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.tickers:
        tickers = [x.strip() for x in args.tickers.split(",") if x.strip()]
        if not tickers:
            raise ValueError("--tickers 有提供，但內容為空")

        weights = None
        if args.weights:
            try:
                weights = [float(x.strip()) for x in args.weights.split(",") if x.strip()]
            except ValueError as e:
                raise ValueError("--weights 需為數字，格式如 0.5,0.3,0.2") from e
            if not weights:
                raise ValueError("--weights 有提供，但內容為空")

        result = run_portfolio(
            tickers=tickers,
            start=args.start,
            end=args.end,
            total_capital=args.capital,
            short_window=args.short_window,
            long_window=args.long_window,
            weights=weights,
        )

        print("=== 投組回測結果 ===")
        print(f"股票: {', '.join(result['tickers'])}")
        print(f"回測區間: {args.start} ~ {args.end}")
        print(f"啟動資金: {args.capital:,.0f}")
        if args.weights:
            print("資金配置模式: 自訂權重")
        else:
            print("資金配置模式: 等權重")
        print(f"回測結束資產總值: {result['portfolio_final_assets']:,.2f}")
        print(f"回測總報酬率: {result['portfolio_return'] * 100:.2f}%")
        print()
        print("=== 各股票明細 ===")
        for ticker in result["tickers"]:
            stock = result["per_stock"][ticker]
            print(
                f"{ticker} | 權重 {stock['weight'] * 100:.2f}% | 配置資金 {stock['allocated_capital']:,.2f} | "
                f"報酬率 {stock['total_return'] * 100:.2f}% | "
                f"持股 {stock['final_shares']:,} | 最新價 {stock['latest_price']:,.2f} | "
                f"股票現值 {stock['current_stock_value']:,.2f} | 銀行餘額 {stock['current_bank_balance']:,.2f} | "
                f"目前總資產 {stock['current_total_assets']:,.2f}"
            )
        print()
        print("=== 目前投組資產估值（使用最新市價）===")
        print(f"股票現值合計: {result['portfolio_current_stock_value']:,.2f}")
        print(f"銀行餘額合計: {result['portfolio_current_bank_balance']:,.2f}")
        print(f"目前總資產: {result['portfolio_current_total_assets']:,.2f}")
        return

    if not args.ticker:
        raise ValueError("請提供 --ticker 或 --tickers")

    ticker = normalize_tw_ticker(args.ticker)

    data = fetch_history(ticker, args.start, args.end)
    signal = moving_average_signal(data, args.short_window, args.long_window)

    backtester = Backtester(initial_capital=args.capital)
    result = backtester.run(data, signal)

    latest_price = fetch_latest_price(ticker)
    final_shares = int(result["history"]["shares"].iloc[-1])
    current_stock_value = final_shares * latest_price
    current_bank_balance = float(result["final_bank_balance"])
    current_total_assets = current_bank_balance + current_stock_value

    print("=== 回測結果 ===")
    print(f"股票: {ticker}")
    print(f"回測區間: {args.start} ~ {args.end}")
    print(f"啟動資金: {args.capital:,.0f}")
    print(f"回測結束資產總值: {result['final_total_assets']:,.2f}")
    print(f"回測總報酬率: {result['total_return'] * 100:.2f}%")
    print()

    print("=== 目前資產估值（使用最新市價）===")
    print(f"最新價格: {latest_price:,.2f}")
    print(f"持股數: {final_shares:,}")
    print(f"股票現值: {current_stock_value:,.2f}")
    print(f"銀行餘額: {current_bank_balance:,.2f}")
    print(f"目前總資產: {current_total_assets:,.2f}")


if __name__ == "__main__":
    main()
