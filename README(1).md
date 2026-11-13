# Trading Systems — Code Samples

Sample code showing my approach to building trading tools. These are **structural examples**, not production-ready systems.

## Files

### `alert_sample.py` — Telegram Alerts
- HTML-formatted messages with inline keyboard buttons
- Retry logic with exponential backoff
- Rate limit handling (429)
- Exception handler with traceback

**What it shows:** How I build monitoring bots that track errors in trading systems and send Telegram alerts.

### `backtest_sample.py` — Backtest Framework
- Commission and slippage modeling (fee bps, slippage bps)
- Gap stop vs intraday stop logic
- Metrics: Sharpe, Sortino, Max Drawdown, CAGR
- Annual/monthly distribution

**What it shows:** How I run honest backtests with realistic costs, not just "buy and hold" curves.

### `l2_collector_sample.py` — L2 Order Book Collector (Python)
- WebSocket connection to OKX public books channel
- Snapshot + incremental delta parsing
- seqId gap detection and resync
- CSV export: microstructure metrics + long format

**What it shows:** How I collect L2 market data for analysis.

### `l2_collector_sample.rs` — L2 Order Book Collector (Rust)
- Same structure as Python version, in Rust
- Auto-reconnect with exponential backoff
- Ping/pong keepalive

**What it shows:** How I build high-performance data collectors in Rust.

### `trading_bot_sample.py` — Telegram Trading Bot
- aiogram 3 + CCXT for spot trading
- Commands: /price, /balance, /limit, /market, /orders, /cancel
- Order confirmation via inline keyboard buttons
- Error handling with retry logic
- Supports Binance, Bybit, OKX, Bitget via CCXT

**What it shows:** How I build full trading bots with control panels and safety features.

## Related Projects

### [S6 Backtest Report](https://github.com/mihamiha0w3-ship-it/S6_backtest)
Full backtest report (PDF) with:
- 99 instruments (crypto + stocks)
- 12,338 portfolio days
- Profit factor 1.71, Sharpe 0.74, Max DD -34.9%
- Commissions and slippage modelled
- Year-by-year stability analysis

## My Services

- **Trading strategies** for crypto markets — if a market has an API, I build a strategy for it
- **Backtests** with commissions and slippage modelled
- **Bot migration** between exchanges: Binance, Bybit, OKX
- **Full trading bots** with control panels: start/stop, status, positions, settings
- **Monitoring bots** with Telegram alerts — missed stop-loss, failed orders
- **L2 order-book collectors** in Rust with CSV export
- **Bug fixing** — API failures, WebSocket reconnects, anything exchange-connected

**Tech stack:** Python, Rust, C++, CCXT, aiogram, pandas, numpy, WebSocket APIs

**Development only.** No signals, no pre-made strategies, no account management, no profit guarantees.
