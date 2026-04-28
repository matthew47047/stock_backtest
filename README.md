# 台股模擬交易與回測系統（Python）

這個專案提供一個可執行的最小版本，支援：

- 連線真實市場資料（使用 `yfinance`）
- 設定啟動資金
- 回測選股/進出策略（範例：均線策略）
- 計算當前股票現值、銀行餘額、總資產

## 1) 安裝

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) 執行回測

```bash
python main.py --ticker 2330 --start 2024-01-01 --end 2025-01-01 --capital 1000000
```

PowerShell 一鍵版（自動建立 `.venv` + 安裝套件 + 執行）：

```powershell
.\run_backtest.ps1 -Ticker 2330 -Start 2024-01-01 -End 2025-01-01 -Capital 1000000
```

多檔（平均分配資金）：

```bash
python main.py --tickers 2330,2317,2454 --start 2024-01-01 --end 2025-01-01 --capital 1000000
```

PowerShell 一鍵版（多檔）：

```powershell
.\run_backtest.ps1 -Tickers 2330,2317,2454 -Start 2024-01-01 -End 2025-01-01 -Capital 1000000
```

參數說明：

- `--ticker`：股票代號，例 `2330`（預設會轉成 `2330.TW`）
- `--tickers`：多檔股票代號（逗號分隔）
- `--start` / `--end`：回測日期範圍（YYYY-MM-DD）
- `--capital`：啟動資金
- `--short-window` / `--long-window`：策略均線參數

## 3) 注意事項

- yfinance 資料可能有延遲，並非券商等級即時報價。
- 上市通常使用 `.TW`，上櫃可能需改成 `.TWO`（例如 `6488.TWO`）。
- 目前範例策略是「全倉買賣 + 單一股票」，可再擴充多檔持股與風控規則。

## 4) 下一步可擴充

- 支援多檔同時回測與資金配置
- 加入停損/停利與最大回撤控制
- 匯出交易明細與績效圖表
- 接入官方資料源（TWSE/TPEx API）或券商 API（若你有憑證）
